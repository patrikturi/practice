"""Step 2: Pydantic validation for note models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from knowledge_mcp.models import NoteCreate, NoteSearchQuery


def test_note_create_accepts_valid_payload() -> None:
    note = NoteCreate(
        title="Ship MCP lesson",
        body="Write the progressive curriculum.",
        tags=["mcp", "learning"],
        priority="high",
    )
    assert note.priority == "high"
    assert note.tags == ["mcp", "learning"]


def test_note_create_rejects_empty_title() -> None:
    with pytest.raises(ValidationError):
        NoteCreate(title="", body="body")


def test_note_create_rejects_bad_tag() -> None:
    with pytest.raises(ValidationError):
        NoteCreate(title="t", body="b", tags=["Bad Tag!"])


def test_search_query_defaults() -> None:
    q = NoteSearchQuery()
    assert q.limit == 20
    assert q.query is None
