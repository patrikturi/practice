"""MCP resources for reading notes (Step 3)."""

from __future__ import annotations

import json

from mcp.server import MCPServer

from knowledge_mcp.db import NoteRepository


def register_resources(mcp: MCPServer, repo: NoteRepository) -> None:
    """Attach read-only note resources to the server."""

    @mcp.resource(
        "notes://list",
        title="All notes",
        description="JSON list of notes (id, title, tags, priority).",
        mime_type="application/json",
    )
    def list_notes_resource() -> str:
        notes = repo.list_notes(limit=100)
        payload = [
            {
                "id": n.id,
                "title": n.title,
                "tags": n.tags,
                "priority": n.priority,
                "uri": f"note://{n.id}",
            }
            for n in notes
        ]
        return json.dumps(payload, indent=2)

    @mcp.resource(
        "note://{note_id}",
        title="Note by id",
        description="Full note content as Markdown.",
        mime_type="text/markdown",
    )
    def note_resource(note_id: str) -> str:
        note = repo.get(note_id)
        if note is None:
            return f"# Note not found\n\nNo note with id `{note_id}`."
        tags = ", ".join(note.tags) if note.tags else "(none)"
        source = f"\n\nSource: {note.source_url}" if note.source_url else ""
        return (
            f"# {note.title}\n\n"
            f"- **id:** `{note.id}`\n"
            f"- **priority:** {note.priority}\n"
            f"- **tags:** {tags}\n"
            f"- **updated:** {note.updated_at.isoformat()}\n\n"
            f"{note.body}{source}\n"
        )
