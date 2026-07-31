"""Backup engine."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class BackupEngine:
    def __init__(self) -> None:
        self._backups: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create_backup(self, name: str, source: str, destination: str) -> Dict[str, Any]:
        import uuid
        bid = str(uuid.uuid4())[:8]
        backup = {"backup_id": bid, "name": name, "source": source, "destination": destination, "status": "completed", "size_mb": 500, "timestamp": time.time()}
        self._backups[bid] = backup
        return backup
    def get_backup(self, backup_id: str) -> Dict[str, Any]:
        return self._backups.get(backup_id, {"error": "not_found"})
    def restore(self, backup_id: str) -> Dict[str, Any]:
        if backup_id not in self._backups:
            return {"error": "not_found"}
        return {"backup_id": backup_id, "status": "restored"}
    def list_backups(self, source: str = "", limit: int = 20) -> List[Dict[str, Any]]:
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
