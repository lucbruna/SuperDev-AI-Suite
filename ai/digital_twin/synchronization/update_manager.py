"""Update manager."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class UpdateManager:
    def __init__(self) -> None:
        self._updates: List[Dict[str, Any]] = []
        self._pending: List[Dict[str, Any]] = []
    def queue_update(self, entity_id: str, field: str, old_value: Any, new_value: Any) -> Dict[str, Any]:
        update = {"entity_id": entity_id, "field": field, "old_value": old_value, "new_value": new_value, "status": "pending", "timestamp": time.time()}
        self._pending.append(update)
        return update
    def apply(self, update_index: int = 0) -> Dict[str, Any]:
        if not self._pending:
            return {"error": "no_pending"}
        update = self._pending.pop(update_index)
        update["status"] = "applied"
        self._updates.append(update)
        return update
    def apply_all(self) -> List[Dict[str, Any]]:
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
    def get_pending(self) -> List[Dict[str, Any]]:
        return self._pending
    def get_applied(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._updates[-limit:]
    def pending_count(self) -> int:
        return len(self._pending)
    def applied_count(self) -> int:
        return len(self._updates)
