"""Steps 1/5/7: tool behavior via in-memory MCP Client."""

from __future__ import annotations

from pathlib import Path

import pytest
from mcp import Client

from knowledge_mcp.db import NoteRepository
from knowledge_mcp.server import create_server


@pytest.fixture
def repo(tmp_path: Path) -> NoteRepository:
    return NoteRepository(tmp_path / "notes.db")


@pytest.fixture
def server(repo: NoteRepository):
    return create_server(repo)


async def test_ping(server) -> None:
    async with Client(server) as client:
        result = await client.call_tool("ping", {})
        assert result.is_error is False
        assert "pong" in str(result.content).lower() or "pong" in str(
            result.structured_content
        ).lower()


async def test_create_list_search_delete(server) -> None:
    async with Client(server) as client:
        created = await client.call_tool(
            "create_note",
            {
                "note": {
                    "title": "Typed tools",
                    "body": "Pydantic validates inputs.",
                    "tags": ["python"],
                    "priority": "medium",
                }
            },
        )
        assert created.is_error is False
        note = created.structured_content
        assert note is not None
        note_id = note["id"]

        listed = await client.call_tool("list_notes", {"limit": 10})
        assert listed.structured_content["total"] >= 1

        searched = await client.call_tool(
            "search_notes",
            {"query": {"query": "Pydantic", "tag": "python", "limit": 10}},
        )
        assert searched.structured_content["total"] >= 1

        got = await client.call_tool("get_note", {"note_id": note_id})
        assert got.structured_content["title"] == "Typed tools"

        deleted = await client.call_tool("delete_note", {"note_id": note_id})
        assert deleted.structured_content["deleted"] is True


async def test_get_missing_note_errors(server) -> None:
    async with Client(server) as client:
        result = await client.call_tool("get_note", {"note_id": "missing-id"})
        assert result.is_error is True
