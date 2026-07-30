from __future__ import annotations

from typing import Any
from datetime import datetime, timezone


class Backup:
    """Manages database backup operations."""

    def __init__(self) -> None:
        self._backups: dict[str, dict[str, Any]] = {}
        self._schedules: dict[str, dict[str, Any]] = {}

    def create_backup(
        self,
        name: str,
        tables: list[str] | None = None,
    ) -> str:
        bid = f"bkp_{len(self._backups) + 1:04d}"
        self._backups[bid] = {
            "id": bid,
            "name": name,
            "tables": tables or [],
            "status": "completed",
            "size_mb": round(len(name) * 10.5, 2),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return bid

    def get_backup(self, backup_id: str) -> dict[str, Any] | None:
        return self._backups.get(backup_id)

    def list_backups(self) -> list[dict[str, Any]]:
        return list(self._backups.values())

    @property
    def backup_count(self) -> int:
        return len(self._backups)

    def schedule_backup(self, cron: str, tables: list[str] | None = None) -> str:
        sid = f"sch_{len(self._schedules) + 1:04d}"
        self._schedules[sid] = {
            "id": sid,
            "cron": cron,
            "tables": tables or [],
            "active": True,
        }
        return sid

    @property
    def scheduled_count(self) -> int:
        return len(self._schedules)

    def to_dict(self) -> dict[str, Any]:
        return {
            "backups": list(self._backups.values()),
            "schedules": list(self._schedules.values()),
            "backup_count": self.backup_count,
            "scheduled_count": self.scheduled_count,
        }
