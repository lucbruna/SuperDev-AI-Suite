"""SQLite store — key/value persistence in a single ``documents`` table.

The default backend when ``storage_backend == "sqlite"``. Payloads are stored
as JSON blobs with a created timestamp; the table is created on first use so
the store works with zero external setup.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from modules.ai_code_knowledge_graph.storage.store import Store

_CREATE = """
CREATE TABLE IF NOT EXISTS documents (
    key        TEXT PRIMARY KEY,
    payload    TEXT NOT NULL,
    created_at REAL NOT NULL
)
"""


class SqliteStore:
    """Key/value store backed by a SQLite database."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute(_CREATE)
        self._conn.commit()

    def save(self, key: str, payload: dict[str, Any]) -> None:
        blob = json.dumps(payload, ensure_ascii=False)
        self._conn.execute(
            "INSERT OR REPLACE INTO documents (key, payload, created_at) VALUES (?, ?, ?)",
            (key, blob, time.time()),
        )
        self._conn.commit()

    def load(self, key: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT payload FROM documents WHERE key = ?", (key,)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def delete(self, key: str) -> bool:
        cursor = self._conn.execute("DELETE FROM documents WHERE key = ?", (key,))
        self._conn.commit()
        return cursor.rowcount > 0

    def exists(self, key: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM documents WHERE key = ?", (key,)
        ).fetchone()
        return row is not None

    def list_keys(self, prefix: str = "") -> list[str]:
        rows = self._conn.execute(
            "SELECT key FROM documents WHERE key LIKE ? ORDER BY key",
            (f"{prefix}%",),
        ).fetchall()
        return [row[0] for row in rows]

    def clear(self) -> None:
        self._conn.execute("DELETE FROM documents")
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
