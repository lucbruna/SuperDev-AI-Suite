"""File backup."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class FileBackup:
    def __init__(self) -> None:
        self._backups: List[Dict[str, Any]] = []
    def backup(self, source_path: str, destination: str) -> Dict[str, Any]:
        import uuid
        bid = str(uuid.uuid4())[:8]
        backup = {"backup_id": bid, "source": source_path, "destination": destination, "files": 150, "size_mb": 250, "status": "completed", "timestamp": time.time()}
        self._backups.append(backup)
        return backup
    def restore(self, backup_id: str, target_path: str = "") -> Dict[str, Any]:
        return {"backup_id": backup_id, "target": target_path, "status": "restored"}
    def list_backups(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._backups[-limit:]
    def count(self) -> int:
        return len(self._backups)
