"""Subscription engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class SubscriptionEngine:
    def __init__(self) -> None:
        self._subscriptions: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create(self, org_id: str, plan_id: str, billing_cycle: str = "monthly") -> Dict[str, Any]:
        import uuid
        sub_id = str(uuid.uuid4())[:8]
        sub = {"id": sub_id, "org_id": org_id, "plan_id": plan_id, "status": "active", "billing_cycle": billing_cycle, "start_date": time.time(), "auto_renew": True}
        self._subscriptions[sub_id] = sub
        return sub
    def get(self, sub_id: str) -> Optional[Dict[str, Any]]:
        return self._subscriptions.get(sub_id)
    def cancel(self, sub_id: str) -> bool:
        sub = self._subscriptions.get(sub_id)
        if sub:
            sub["status"] = "cancelled"
            sub["cancelled_at"] = time.time()
            return True
        return False
    def list_by_org(self, org_id: str) -> List[Dict[str, Any]]:
        return [s for s in self._subscriptions.values() if s["org_id"] == org_id]
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._subscriptions.values())
    def count(self) -> int:
        return len(self._subscriptions)
    def is_running(self) -> bool:
        return self._started
