"""MCP prompts for note workflows (Step 4)."""

from __future__ import annotations

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver.prompts.base import AssistantMessage, Message, UserMessage
from pydantic import Field

from knowledge_mcp.db import NoteRepository


def register_prompts(mcp: MCPServer, repo: NoteRepository) -> None:
    """Attach reusable prompt templates."""

    @mcp.prompt(title="Summarize note")
    def summarize_note(
        note_id: Annotated[str, Field(description="Id of the note to summarize.")],
    ) -> list[Message]:
        """Build a summarization prompt from a stored note."""
        note = repo.get(note_id)
        if note is None:
            return [
                UserMessage(f"There is no note with id `{note_id}`. Ask me for a valid id."),
            ]
        return [
            UserMessage(
                "Summarize the following personal note in 3 bullet points. "
                "Keep any action items."
            ),
            UserMessage(f"# {note.title}\n\n{note.body}"),
            AssistantMessage("Here is a concise summary of your note:"),
        ]

    @mcp.prompt(title="Weekly review")
    def weekly_review(
        focus: Annotated[
            str,
            Field(description="Optional theme for the review, e.g. 'shipping'."),
        ] = "general progress",
    ) -> list[Message]:
        """Seed a weekly review conversation from recent notes."""
        notes = repo.list_notes(limit=10)
        if not notes:
            body = "(No notes yet — create a few with create_note first.)"
        else:
            lines = [
                f"- [{n.priority}] {n.title} (tags: {', '.join(n.tags) or 'none'}; id={n.id})"
                for n in notes
            ]
            body = "\n".join(lines)

        return [
            UserMessage(
                f"Help me do a weekly review focused on: {focus}.\n\n"
                f"Here are my recent notes:\n{body}\n\n"
                "Ask clarifying questions, then propose priorities for next week."
            ),
        ]
