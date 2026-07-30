from __future__ import annotations

import json
import sqlite3
from typing import Any


class SqliteStorage:
    """SQLite-backed storage for monitoring data."""

    def __init__(self, db_path: str = "monitoring.db") -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS monitoring_data "
            "(key TEXT PRIMARY KEY, value TEXT, updated_at REAL)"
        )
        self._conn.commit()

    def store(self, key: str, data: dict[str, Any]) -> None:
        import time
        self._conn.execute(
            "INSERT OR REPLACE INTO monitoring_data (key, value, updated_at) "
            "VALUES (?, ?, ?)",
            (key, json.dumps(data, default=str), time.time()),
        )
        self._conn.commit()

    def retrieve(self, key: str) -> dict[str, Any] | None:
        cur = self._conn.execute(
            "SELECT value FROM monitoring_data WHERE key = ?", (key,)
        )
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def delete(self, key: str) -> bool:
        cur = self._conn.execute(
            "DELETE FROM monitoring_data WHERE key = ?", (key,)
        )
        self._conn.commit()
        return cur.rowcount > 0

    def list_keys(self) -> list[str]:
        cur = self._conn.execute("SELECT key FROM monitoring_data")
        return [row[0] for row in cur.fetchall()]

    def close(self) -> None:
        self._conn.close()
