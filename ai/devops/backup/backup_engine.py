"""Backup engine."""
from __future__ import annotations

import time
from typing import Any


class BackupEngine:
    def __init__(self) -> None:
        self._backups: dict[str, dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create_backup(self, name: str, source: str, destination: str) -> dict[str, Any]:
        import uuid
        bid = str(uuid.uuid4())[:8]
        backup = {"backup_id": bid, "name": name, "source": source, "destination": destination, "status": "completed", "size_mb": 500, "timestamp": time.time()}
        self._backups[bid] = backup
        return backup
    def get_backup(self, backup_id: str) -> dict[str, Any]:
        return self._backups.get(backup_id, {"error": "not_found"})
    def restore(self, backup_id: str) -> dict[str, Any]:
        if backup_id not in self._backups:
            return {"error": "not_found"}
        return {"backup_id": backup_id, "status": "restored"}
    def list_backups(self, source: str = "", limit: int = 20) -> list[dict[str, Any]]:
        backups = list(self._backups.values())
        if source:
            backups = [b for b in backups if b.get("source") == source]
        return backups[-limit:]
    def delete_backup(self, backup_id: str) -> bool:
        if backup_id in self._backups:
            del self._backups[backup_id]
            return True
        return False
    def count(self) -> int:
        return len(self._backups)
    def is_running(self) -> bool:
        return self._started
