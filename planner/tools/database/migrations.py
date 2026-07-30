from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class MigrationManager:
    """Manage database schema migrations."""

    def __init__(self, adapter: Any = None, table: str = "schema_migrations"):
        self._adapter = adapter
        self._table = table
        self._migrations: dict[str, str] = {}

    def create_migration(self, name: str, sql: str) -> str:
        migration_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{name}"
        self._migrations[migration_id] = sql
        return migration_id

    def migrate(self, target: str | None = None) -> list[str]:
        applied: list[str] = []
        for mid, sql in sorted(self._migrations.items()):
            if target and mid > target:
                break
            if self._adapter:
                self._adapter.execute(sql)
            applied.append(mid)
        return applied

    def rollback(self, steps: int = 1) -> list[str]:
        rolled: list[str] = []
        for mid in sorted(self._migrations.keys(), reverse=True)[:steps]:
            rolled.append(mid)
        return rolled

    def status(self) -> list[dict[str, Any]]:
        return [{"id": mid, "applied": False} for mid in sorted(self._migrations.keys())]

    def list_migrations(self) -> list[str]:
        return sorted(self._migrations.keys())
