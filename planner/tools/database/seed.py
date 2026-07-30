from __future__ import annotations

import json
from typing import Any

from .database_tool import DatabaseTool


class DatabaseSeeder:
    """Seed database tables with initial data."""

    def __init__(self, adapter: DatabaseTool):
        self._adapter = adapter

    def seed_table(self, table: str, rows: list[dict[str, Any]]) -> int:
        for row in rows:
            cols = ", ".join(row.keys())
            placeholders = ", ".join("?" for _ in row)
            values = list(row.values())
            self._adapter.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", row)
        return len(rows)

    def truncate(self, *tables: str) -> None:
        for table in tables:
            self._adapter.execute(f"DELETE FROM {table}")

    def seed_from_json(self, filepath: str) -> dict[str, int]:
        with open(filepath) as f:
            data = json.load(f)
        results: dict[str, int] = {}
        for table, rows in data.items():
            results[table] = self.seed_table(table, rows)
        return results
