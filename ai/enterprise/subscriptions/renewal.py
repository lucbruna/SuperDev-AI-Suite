"""Subscription renewal."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class RenewalManager:
    def __init__(self) -> None:
        self._renewals: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []
    def schedule_renewal(self, subscription_id: str, next_date: float, amount: float) -> Dict[str, Any]:
        renewal = {"subscription_id": subscription_id, "next_date": next_date, "amount": amount, "status": "scheduled"}
        self._renewals[subscription_id] = renewal
        return renewal
    def process_renewal(self, subscription_id: str) -> Dict[str, Any]:
        renewal = self._renewals.get(subscription_id)
        if not renewal:
            return {"error": "not_found"}
        renewal["status"] = "completed"
        renewal["processed_at"] = time.time()
        self._history.append(dict(renewal))
        return renewal
    def cancel_renewal(self, subscription_id: str) -> bool:
        if subscription_id in self._renewals:
            self._renewals[subscription_id]["status"] = "cancelled"
            return True
        return False
    def get_renewal(self, subscription_id: str) -> Dict[str, Any]:
        return self._renewals.get(subscription_id, {})
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._history[-limit:]
    def get_pending(self) -> List[Dict[str, Any]]:
        return [r for r in self._renewals.values() if r["status"] == "scheduled"]
