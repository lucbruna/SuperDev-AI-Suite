from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .database_tool import DatabaseTool


class DatabaseBackup:
    """Database backup and restore operations."""

    def __init__(self, adapter: DatabaseTool):
        self._adapter = adapter
        self._snapshots: dict[str, list[dict[str, Any]]] = {}

    def dump(self, tables: list[str] | None = None) -> str:
        snapshot_id = f"snap_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        data: list[dict[str, Any]] = []
        for table in tables or []:
            rows = self._adapter.execute(f"SELECT * FROM {table}")
            data.append({"table": table, "rows": rows})
        self._snapshots[snapshot_id] = data
        return snapshot_id

    def restore(self, snapshot_id: str) -> int:
        data = self._snapshots.get(snapshot_id, [])
        count = 0
        for entry in data:
            for row in entry["rows"]:
                count += 1
        return count

    def list_snapshots(self) -> list[str]:
        return list(self._snapshots.keys())

    def verify(self, snapshot_id: str) -> bool:
        return snapshot_id in self._snapshots
