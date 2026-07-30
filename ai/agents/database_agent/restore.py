from __future__ import annotations

from typing import Any
from datetime import datetime, timezone


class Restore:
    """Manages database restore operations."""

    def __init__(self) -> None:
        self._restores: dict[str, dict[str, Any]] = {}

    def restore_from_backup(
        self,
        backup_id: str,
        tables: list[str] | None = None,
    ) -> str:
        rid = f"rst_{len(self._restores) + 1:04d}"
        self._restores[rid] = {
            "id": rid,
            "backup_id": backup_id,
            "tables": tables or [],
            "status": "completed",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        return rid

    def get_restore(self, restore_id: str) -> dict[str, Any] | None:
        return self._restores.get(restore_id)

    def list_restores(self) -> list[dict[str, Any]]:
        return list(self._restores.values())

    @property
    def restore_count(self) -> int:
        return len(self._restores)

    def dry_run(self, backup_id: str) -> dict[str, Any]:
        return {
            "backup_id": backup_id,
            "will_restore": True,
            "estimated_size_mb": 42.0,
            "estimated_duration_sec": 15,
            "tables_to_restore": 5,
            "warnings": ["Foreign key checks will be disabled"],
        }

    def validate_backup(self, backup_id: str) -> bool:
        return backup_id.startswith("bkp_")

    def to_dict(self) -> dict[str, Any]:
        return {
            "restores": list(self._restores.values()),
            "restore_count": self.restore_count,
        }
