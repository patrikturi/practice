"""SQLite persistence for notes (Step 5)."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

from knowledge_mcp.models import Note, NoteCreate, NoteSearchQuery


def default_db_path() -> Path:
    env = os.environ.get("KNOWLEDGE_MCP_DB")
    if env:
        return Path(env).expanduser().resolve()
    return Path.cwd() / "data" / "notes.db"


class NoteRepository:
    """Thin SQLite repository — no ORM, focus stays on MCP."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        if db_path is None:
            self.db_path: Path | str = default_db_path()
        elif db_path == ":memory:" or db_path == Path(":memory:"):
            self.db_path = ":memory:"
        else:
            self.db_path = Path(db_path)
        self._memory = self.db_path == ":memory:"
        if not self._memory:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        if self._memory:
            if self._conn is None:
                self._conn = sqlite3.connect(":memory:", check_same_thread=False)
                self._conn.row_factory = sqlite3.Row
            return self._conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    tags TEXT NOT NULL DEFAULT '[]',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    source_url TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at DESC)"
            )
            conn.commit()
        finally:
            if not self._memory:
                conn.close()

    def _row_to_note(self, row: sqlite3.Row) -> Note:
        return Note(
            id=row["id"],
            title=row["title"],
            body=row["body"],
            tags=json.loads(row["tags"]),
            priority=row["priority"],  # type: ignore[arg-type]
            source_url=row["source_url"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create(self, payload: NoteCreate, *, source_url: str | None = None) -> Note:
        now = datetime.now(UTC)
        note = Note(
            id=str(uuid.uuid4()),
            title=payload.title,
            body=payload.body,
            tags=payload.tags,
            priority=payload.priority,
            source_url=source_url,
            created_at=now,
            updated_at=now,
        )
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO notes (
                    id, title, body, tags, priority, source_url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    note.id,
                    note.title,
                    note.body,
                    json.dumps(note.tags),
                    note.priority,
                    note.source_url,
                    note.created_at.isoformat(),
                    note.updated_at.isoformat(),
                ),
            )
            conn.commit()
        finally:
            if not self._memory:
                conn.close()
        return note

    def get(self, note_id: str) -> Note | None:
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
            return self._row_to_note(row) if row else None
        finally:
            if not self._memory:
                conn.close()

    def list_notes(self, *, limit: int = 50) -> list[Note]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM notes ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [self._row_to_note(row) for row in rows]
        finally:
            if not self._memory:
                conn.close()

    def search(self, query: NoteSearchQuery) -> list[Note]:
        clauses: list[str] = []
        params: list[object] = []

        if query.query:
            clauses.append("(title LIKE ? OR body LIKE ?)")
            like = f"%{query.query}%"
            params.extend([like, like])
        if query.tag:
            # tags stored as JSON array of strings
            clauses.append("EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?)")
            params.append(query.tag)
        if query.priority:
            clauses.append("priority = ?")
            params.append(query.priority)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM notes {where} ORDER BY updated_at DESC LIMIT ?"
        params.append(query.limit)

        conn = self._connect()
        try:
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_note(row) for row in rows]
        finally:
            if not self._memory:
                conn.close()

    def delete(self, note_id: str) -> bool:
        conn = self._connect()
        try:
            cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            if not self._memory:
                conn.close()

    def count(self) -> int:
        conn = self._connect()
        try:
            row = conn.execute("SELECT COUNT(*) AS n FROM notes").fetchone()
            return int(row["n"]) if row else 0
        finally:
            if not self._memory:
                conn.close()
