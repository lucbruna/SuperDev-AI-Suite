"""Restore manager."""
from __future__ import annotations

import time
from typing import Any


class RestoreManager:
    def __init__(self) -> None:
        self._restores: list[dict[str, Any]] = []
    def restore(self, backup_id: str, target: str, options: dict[str, Any] = None) -> dict[str, Any]:
        import uuid
        rid = str(uuid.uuid4())[:8]
        restore = {"restore_id": rid, "backup_id": backup_id, "target": target, "options": options or {}, "status": "completed", "timestamp": time.time()}
        self._restores.append(restore)
        return restore
    def get_restore(self, restore_id: str) -> dict[str, Any]:
        for r in self._restores:
            if r["restore_id"] == restore_id:
                return r
        return {"error": "not_found"}
    def list_restores(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._restores[-limit:]
    def count(self) -> int:
        return len(self._restores)
