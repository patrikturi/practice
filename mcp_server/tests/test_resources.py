"""Step 3: resources and prompts via in-memory MCP Client."""

from __future__ import annotations

from pathlib import Path

import pytest
from mcp import Client

from knowledge_mcp.db import NoteRepository
from knowledge_mcp.models import NoteCreate
from knowledge_mcp.server import create_server


@pytest.fixture
def repo(tmp_path: Path) -> NoteRepository:
    return NoteRepository(tmp_path / "notes.db")


@pytest.fixture
def server(repo: NoteRepository):
    return create_server(repo)


async def test_note_resource(server, repo: NoteRepository) -> None:
    note = repo.create(
        NoteCreate(title="Resource note", body="Readable via URI.", tags=["res"])
    )
    async with Client(server) as client:
        listed = await client.read_resource("notes://list")
        assert note.id in listed.contents[0].text

        content = await client.read_resource(f"note://{note.id}")
        text = content.contents[0].text
        assert "Resource note" in text
        assert "Readable via URI." in text


async def test_summarize_prompt(server, repo: NoteRepository) -> None:
    note = repo.create(
        NoteCreate(title="Prompt note", body="Teach prompts vs tools.", tags=["mcp"])
    )
    async with Client(server) as client:
        prompts = await client.list_prompts()
        names = {p.name for p in prompts.prompts}
        assert "summarize_note" in names
        assert "weekly_review" in names

        rendered = await client.get_prompt("summarize_note", {"note_id": note.id})
        assert rendered.messages
        blob = " ".join(
            getattr(m.content, "text", "") or "" for m in rendered.messages
        )
        assert "Prompt note" in blob
