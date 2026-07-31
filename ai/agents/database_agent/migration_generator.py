from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class MigrationGenerator:
    """Generates and manages database migrations."""

    def __init__(self) -> None:
        self._migrations: dict[str, dict[str, Any]] = {}

    def create_migration(self, name: str, up_sql: str, down_sql: str) -> str:
        mid = f"mig_{len(self._migrations) + 1:04d}"
        self._migrations[mid] = {
            "id": mid,
            "name": name,
            "up_sql": up_sql,
            "down_sql": down_sql,
            "applied": False,
            "created_at": datetime.now(UTC).isoformat(),
        }
        return mid

    def get_migration(self, migration_id: str) -> dict[str, Any] | None:
        return self._migrations.get(migration_id)

    def list_migrations(self) -> list[dict[str, Any]]:
        return list(self._migrations.values())

    @property
    def migration_count(self) -> int:
        return len(self._migrations)

    def apply_migrations(self, limit: int | None = None) -> list[dict[str, Any]]:
        applied = []
        for m in self._migrations.values():
            if limit and len(applied) >= limit:
                break
            if not m["applied"]:
                m["applied"] = True
                applied.append(m)
        return applied

    def rollback_migrations(self, count: int = 1) -> list[dict[str, Any]]:
        rolled = []
        for m in reversed(list(self._migrations.values())):
            if len(rolled) >= count:
                break
            if m["applied"]:
                m["applied"] = False
                rolled.append(m)
        return rolled

    @property
    def pending_count(self) -> int:
        return sum(1 for m in self._migrations.values() if not m["applied"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "migrations": list(self._migrations.values()),
            "migration_count": self.migration_count,
            "pending_count": self.pending_count,
        }
