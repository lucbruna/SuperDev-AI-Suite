"""Subscription downgrade."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class DowngradeManager:
    def __init__(self) -> None:
        self._downgrades: List[Dict[str, Any]] = []
    def downgrade(self, subscription_id: str, from_plan: str, to_plan: str, reason: str = "") -> Dict[str, Any]:
        entry = {"subscription_id": subscription_id, "from_plan": from_plan, "to_plan": to_plan, "reason": reason, "downgraded_at": time.time()}
        self._downgrades.append(entry)
        return entry
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._downgrades)
    def get_by_subscription(self, subscription_id: str) -> List[Dict[str, Any]]:
        return [d for d in self._downgrades if d["subscription_id"] == subscription_id]
    def count(self) -> int:
        return len(self._downgrades)
    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._downgrades[-limit:]
