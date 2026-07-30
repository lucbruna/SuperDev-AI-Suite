from __future__ import annotations

from typing import Any

from .backup import DatabaseBackup
from .database_tool import DatabaseTool


class DatabaseRestore:
    """Restore database from backups."""

    def __init__(self, backup_service: DatabaseBackup | None = None):
        self.backup_service = backup_service

    def restore_from_backup(self, snapshot_id: str) -> int:
        if self.backup_service is None:
            return 0
        return self.backup_service.restore(snapshot_id)

    def verify_backup(self, snapshot_id: str) -> dict[str, Any]:
        if self.backup_service is None:
            return {"exists": False, "valid": False}
        return {
            "exists": self.backup_service.verify(snapshot_id),
            "valid": True,
        }

    def rollback(self, snapshot_id: str) -> dict[str, Any]:
        count = self.restore_from_backup(snapshot_id)
        return {"status": "success" if count > 0 else "failed", "snapshot_id": snapshot_id}
