from __future__ import annotations

from typing import Any

from .backup import VectorBackup


class VectorRestore:
    """Restore vectors from backups."""

    def __init__(self, backup_service: VectorBackup | None = None):
        self.backup_service = backup_service or VectorBackup()

    def restore_from_backup(self, backup_id: str) -> dict[str, list[float]] | None:
        backup = self.backup_service.get_backup(backup_id)
        if backup is None:
            return None
        return {k: list(v) for k, v in backup.get("vectors", {}).items()}

    def verify_backup(self, backup_id: str) -> dict[str, Any]:
        backup = self.backup_service.get_backup(backup_id)
        if backup is None:
            return {"exists": False, "valid": False}
        return {
            "exists": True,
            "valid": True,
            "vector_count": backup["vector_count"],
            "timestamp": backup["timestamp"],
        }

    def rollback(self, backup_id: str) -> dict[str, Any]:
        vectors = self.restore_from_backup(backup_id)
        if vectors is None:
            return {"status": "failed", "reason": "backup_not_found"}
        return {"status": "success", "vectors_restored": len(vectors), "backup_id": backup_id}
