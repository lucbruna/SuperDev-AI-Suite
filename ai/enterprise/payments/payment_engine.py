"""Payment engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class PaymentEngine:
    def __init__(self) -> None:
        self._payments: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create(self, org_id: str, amount: float, method: str = "credit_card", currency: str = "BRL") -> Dict[str, Any]:
        import uuid
        pay_id = str(uuid.uuid4())[:8]
        payment = {"id": pay_id, "org_id": org_id, "amount": amount, "method": method, "currency": currency, "status": "pending", "created_at": time.time()}
        self._payments[pay_id] = payment
        return payment
    def get(self, pay_id: str) -> Optional[Dict[str, Any]]:
        return self._payments.get(pay_id)
    def complete(self, pay_id: str) -> bool:
        pay = self._payments.get(pay_id)
        if pay:
            pay["status"] = "completed"
            pay["processed_at"] = time.time()
            return True
        return False
    def fail(self, pay_id: str, reason: str = "") -> bool:
        pay = self._payments.get(pay_id)
        if pay:
            pay["status"] = "failed"
            pay["failure_reason"] = reason
            return True
        return False
    def list_by_org(self, org_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return [p for p in self._payments.values() if p["org_id"] == org_id][-limit:]
    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        return list(self._payments.values())[-limit:]
    def total_by_org(self, org_id: str) -> float:
        return sum(p["amount"] for p in self._payments.values() if p["org_id"] == org_id and p["status"] == "completed")
    def count(self) -> int:
        return len(self._payments)
    def is_running(self) -> bool:
        return self._started
