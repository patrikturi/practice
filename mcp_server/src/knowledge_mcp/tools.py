"""MCP tools for the knowledge base (Steps 1–5)."""

from __future__ import annotations

import re
from html import unescape
from typing import Annotated

import httpx
from mcp.server import MCPServer
from pydantic import Field

from knowledge_mcp.db import NoteRepository
from knowledge_mcp.models import (
    DeleteResult,
    ImportUrlRequest,
    Note,
    NoteCreate,
    NoteList,
    NoteSearchQuery,
)


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_title(html: str, fallback: str) -> str:
    match = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    if not match:
        return fallback
    title = _strip_html(match.group(1))
    return title[:200] or fallback


def register_tools(mcp: MCPServer, repo: NoteRepository) -> None:
    """Attach all knowledge-base tools to the server."""

    @mcp.tool(title="Ping")
    def ping() -> str:
        """Health check — confirms the MCP server is reachable (Step 1)."""
        return "pong from knowledge-mcp"

    @mcp.tool(title="Create note")
    def create_note(note: NoteCreate) -> Note:
        """Create a note with validated title, body, tags, and priority."""
        return repo.create(note)

    @mcp.tool(title="Get note")
    def get_note(
        note_id: Annotated[str, Field(description="Note id returned by create_note.")],
    ) -> Note:
        """Fetch a single note by id."""
        found = repo.get(note_id)
        if found is None:
            raise ValueError(f"Note not found: {note_id}")
        return found

    @mcp.tool(title="List notes")
    def list_notes(
        limit: Annotated[int, Field(default=20, ge=1, le=100, description="Max notes.")] = 20,
    ) -> NoteList:
        """List notes newest-first."""
        notes = repo.list_notes(limit=limit)
        return NoteList(notes=notes, total=repo.count())

    @mcp.tool(title="Search notes")
    def search_notes(query: NoteSearchQuery) -> NoteList:
        """Search notes by text, tag, and/or priority."""
        notes = repo.search(query)
        return NoteList(notes=notes, total=len(notes))

    @mcp.tool(title="Delete note")
    def delete_note(
        note_id: Annotated[str, Field(description="Note id to delete.")],
    ) -> DeleteResult:
        """Delete a note by id."""
        deleted = repo.delete(note_id)
        return DeleteResult(id=note_id, deleted=deleted)

    @mcp.tool(title="Import URL as note")
    def import_url(request: ImportUrlRequest) -> Note:
        """Fetch a URL with httpx and store title + text snippet as a note."""
        url = str(request.url)
        with httpx.Client(follow_redirects=True, timeout=20.0) as client:
            response = client.get(url, headers={"User-Agent": "knowledge-mcp/0.1"})
            response.raise_for_status()
            html = response.text

        title = _extract_title(html, fallback=url)
        body = _strip_html(html)[:4_000]
        if not body:
            body = f"(No extractable text from {url})"

        payload = NoteCreate(
            title=title,
            body=body,
            tags=request.tags,
            priority=request.priority,
        )
        return repo.create(payload, source_url=url)
