from __future__ import annotations

import sqlite3
from typing import Any

from .database_tool import DatabaseTool


class SQLiteAdapter(DatabaseTool):
    """SQLite database adapter."""

    def __init__(self, path: str = ":memory:"):
        super().__init__(path)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        self._conn = sqlite3.connect(self.connection_string)
        self._conn.row_factory = sqlite3.Row
        self._connected = True

    def disconnect(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
        self._connected = False

    def execute(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if self._conn is None:
            raise RuntimeError("Not connected")
        cur = self._conn.execute(query, params or {})
        return [dict(row) for row in cur.fetchall()]

    def execute_many(self, query: str, params_list: list[dict[str, Any]]) -> int:
        if self._conn is None:
            raise RuntimeError("Not connected")
        cur = self._conn.executemany(query, params_list)
        return cur.rowcount

    def get_tables(self) -> list[str]:
        rows = self.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [r["name"] for r in rows]
