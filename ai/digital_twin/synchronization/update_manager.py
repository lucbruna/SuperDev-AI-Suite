"""Update manager."""
from __future__ import annotations

import time
from typing import Any


class UpdateManager:
    def __init__(self) -> None:
        self._updates: list[dict[str, Any]] = []
        self._pending: list[dict[str, Any]] = []
    def queue_update(self, entity_id: str, field: str, old_value: Any, new_value: Any) -> dict[str, Any]:
        update = {"entity_id": entity_id, "field": field, "old_value": old_value, "new_value": new_value, "status": "pending", "timestamp": time.time()}
        self._pending.append(update)
        return update
    def apply(self, update_index: int = 0) -> dict[str, Any]:
        if not self._pending:
            return {"error": "no_pending"}
        update = self._pending.pop(update_index)
        update["status"] = "applied"
        self._updates.append(update)
        return update
    def apply_all(self) -> list[dict[str, Any]]:
        applied = []
        while self._pending:
            applied.append(self.apply())
        return applied
    def rollback(self, update_id: str = "") -> bool:
        if not self._updates:
            return False
        if update_id:
            for i, u in enumerate(self._updates):
                if u.get("entity_id") == update_id:
                    self._updates[i]["status"] = "rolled_back"
                    return True
        return False
    def get_pending(self) -> list[dict[str, Any]]:
        return self._pending
    def get_applied(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._updates[-limit:]
    def pending_count(self) -> int:
        return len(self._pending)
    def applied_count(self) -> int:
        return len(self._updates)
