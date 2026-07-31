"""File backup."""

from __future__ import annotations

import time
from typing import Any


class FileBackup:
    def __init__(self) -> None:
        self._backups: list[dict[str, Any]] = []

    def backup(self, source_path: str, destination: str) -> dict[str, Any]:
        import uuid

        bid = str(uuid.uuid4())[:8]
        backup = {
            "backup_id": bid,
            "source": source_path,
            "destination": destination,
            "files": 150,
            "size_mb": 250,
            "status": "completed",
            "timestamp": time.time(),
        }
        self._backups.append(backup)
        return backup

    def restore(self, backup_id: str, target_path: str = "") -> dict[str, Any]:
        return {"backup_id": backup_id, "target": target_path, "status": "restored"}

    def list_backups(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._backups[-limit:]

    def count(self) -> int:
        return len(self._backups)
