from __future__ import annotations

import json
import os
import time
from typing import Any

from ..database_interfaces import IDatabaseDriver


class BackupManager:
    """Manages database backup and restore operations.

    Supports full exports to JSON/JSONL format for portability.
    """

    def __init__(self, driver: IDatabaseDriver, backup_dir: str = "backups") -> None:
        self._driver = driver
        self._backup_dir = backup_dir

    async def create_backup(self, tables: list[str] | None = None) -> str:
        os.makedirs(self._backup_dir, exist_ok=True)
        timestamp = int(time.time())
        filename = f"backup_{timestamp}.json"
        path = os.path.join(self._backup_dir, filename)
        backup_data: dict[str, Any] = {
            "version": "1.0",
            "created_at": timestamp,
            "dialect": self._driver.dialect,
            "tables": {},
        }
        if tables is None:
            tables = await self._list_tables()
        for table in tables:
            rows = await self._driver.execute_query(f"SELECT * FROM {table}")
            backup_data["tables"][table] = {
                "row_count": len(rows),
                "rows": rows,
            }
        with open(path, "w") as f:
            json.dump(backup_data, f, default=str, indent=2)
        return path

    async def restore(self, path: str, tables: list[str] | None = None) -> int:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Backup not found: {path}")
        with open(path) as f:
            backup_data = json.load(f)
        restored = 0
        for table, data in backup_data.get("tables", {}).items():
            if tables and table not in tables:
                continue
            for row in data.get("rows", []):
                columns = ", ".join(row.keys())
                placeholders = ", ".join("?" for _ in row)
                values = list(row.values())
                q = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                await self._driver.execute(q, values)
                restored += 1
        return restored

    async def _list_tables(self) -> list[str]:
        dialect = self._driver.dialect
        if dialect == "postgresql":
            rows = await self._driver.execute_query(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
            return [r["table_name"] for r in rows]
        elif dialect == "sqlite":
            rows = await self._driver.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            return [r["name"] for r in rows]
        elif dialect in ("mysql", "mariadb"):
            rows = await self._driver.execute_query("SHOW TABLES")
            return list(rows[0].values()) if rows else []
        return []


__all__ = [
    "BackupManager",
]
