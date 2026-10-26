"""Pydantic models for notes (Step 2+)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl


Priority = Literal["low", "medium", "high"]

Tag = Annotated[
    str,
    Field(min_length=1, max_length=32, pattern=r"^[a-z0-9][a-z0-9_-]*$"),
]


class NoteCreate(BaseModel):
    """Payload for creating a note."""

    title: Annotated[str, Field(min_length=1, max_length=200, description="Short note title.")]
    body: Annotated[str, Field(min_length=1, max_length=20_000, description="Note content.")]
    tags: Annotated[
        list[Tag],
        Field(default_factory=list, max_length=20, description="Lowercase tags."),
    ]
    priority: Annotated[Priority, Field(default="medium", description="Relative importance.")]


class Note(NoteCreate):
    """A persisted note."""

    id: Annotated[str, Field(description="Stable note id.")]
    created_at: datetime
    updated_at: datetime
    source_url: Annotated[str | None, Field(default=None, description="Origin URL if imported.")]


class NoteSearchQuery(BaseModel):
    """Search filters for notes."""

    query: Annotated[
        str | None,
        Field(default=None, max_length=200, description="Substring match on title/body."),
    ]
    tag: Annotated[Tag | None, Field(default=None, description="Exact tag match.")]
    priority: Annotated[Priority | None, Field(default=None, description="Filter by priority.")]
    limit: Annotated[int, Field(default=20, ge=1, le=100, description="Max results.")]


class NoteList(BaseModel):
    """List of notes returned by tools."""

    notes: list[Note]
    total: int


class ImportUrlRequest(BaseModel):
    """Fetch a URL and store it as a note."""

    url: Annotated[HttpUrl, Field(description="Page to import.")]
    tags: Annotated[list[Tag], Field(default_factory=list, max_length=20)]
    priority: Annotated[Priority, Field(default="medium")]


class DeleteResult(BaseModel):
    """Result of deleting a note."""

    id: str
    deleted: bool
