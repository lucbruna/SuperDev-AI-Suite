from __future__ import annotations

import json
import time
from typing import Any


class AuditLog:
    """Simple audit trail for database operations.

    Records who did what and when.
    """

    def __init__(self, log_path: str | None = None) -> None:
        self._log_path = log_path
        self._entries: list[dict[str, Any]] = []

    async def record(
        self,
        action: str,
        table: str,
        entity_id: Any = None,
        user: str = "system",
        changes: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "timestamp": time.time(),
            "action": action,  # CREATE, READ, UPDATE, DELETE
            "table": table,
            "entity_id": str(entity_id) if entity_id is not None else None,
            "user": user,
            "changes": changes or {},
            "metadata": metadata or {},
        }
        self._entries.append(entry)
        if self._log_path:
            with open(self._log_path, "a") as f:
                f.write(json.dumps(entry, default=str) + "\n")

    async def search(
        self,
        table: str | None = None,
        action: str | None = None,
        user: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        results = list(self._entries)
        if table:
            results = [e for e in results if e["table"] == table]
        if action:
            results = [e for e in results if e["action"] == action]
        if user:
            results = [e for e in results if e["user"] == user]
        return results[-limit:]

    async def clear(self) -> None:
        self._entries.clear()
        if self._log_path:
            with open(self._log_path, "w") as f:
                f.truncate()


__all__ = [
    "AuditLog",
]
