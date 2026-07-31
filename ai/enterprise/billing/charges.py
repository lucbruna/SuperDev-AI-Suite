"""Charge management."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ChargeManager:
    def __init__(self) -> None:
        self._charges: List[Dict[str, Any]] = []
    def create_charge(self, org_id: str, amount: float, description: str, charge_type: str = "subscription") -> Dict[str, Any]:
        import uuid
        charge = {"id": str(uuid.uuid4())[:8], "org_id": org_id, "amount": amount, "description": description, "type": charge_type, "status": "pending", "created_at": time.time()}
        self._charges.append(charge)
        return charge
    def mark_paid(self, charge_id: str) -> bool:
        for c in self._charges:
            if c["id"] == charge_id:
                c["status"] = "paid"
                c["paid_at"] = time.time()
                return True
        return False
    def mark_failed(self, charge_id: str) -> bool:
        for c in self._charges:
            if c["id"] == charge_id:
                c["status"] = "failed"
                return True
        return False
    def get_charges(self, org_id: str = "", status: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        results = self._charges
        if org_id:
            results = [c for c in results if c["org_id"] == org_id]
        if status:
            results = [c for c in results if c["status"] == status]
        return results[-limit:]
    def total_by_org(self, org_id: str) -> float:
        return sum(c["amount"] for c in self._charges if c["org_id"] == org_id and c["status"] == "paid")
    def count(self) -> int:
        return len(self._charges)
