"""Customer analytics."""
from __future__ import annotations
from typing import Any, Dict, List

class CustomerAnalytics:
    def __init__(self) -> None:
        self._customers: Dict[str, Dict[str, Any]] = {}
    def add_customer(self, org_id: str, plan: str = "starter", mrr: float = 0.0) -> Dict[str, Any]:
        customer = {"org_id": org_id, "plan": plan, "mrr": mrr, "interactions": 0, "tickets": 0}
        self._customers[org_id] = customer
        return customer
    def record_interaction(self, org_id: str) -> None:
        if org_id in self._customers:
            self._customers[org_id]["interactions"] += 1
    def record_ticket(self, org_id: str) -> None:
        if org_id in self._customers:
            self._customers[org_id]["tickets"] += 1
    def get_customer(self, org_id: str) -> Dict[str, Any]:
        return self._customers.get(org_id, {})
    def total_customers(self) -> int:
        return len(self._customers)
    def total_mrr(self) -> float:
        return sum(c.get("mrr", 0) for c in self._customers.values())
    def avg_mrr(self) -> float:
        customers = list(self._customers.values())
        if not customers:
            return 0.0
        return sum(c.get("mrr", 0) for c in customers) / len(customers)
    def by_plan(self) -> Dict[str, int]:
        plans: Dict[str, int] = {}
        for c in self._customers.values():
            p = c.get("plan", "unknown")
            plans[p] = plans.get(p, 0) + 1
        return plans
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._customers.values())
    def update_plan(self, org_id: str, new_plan: str, new_mrr: float) -> bool:
        if org_id in self._customers:
            self._customers[org_id]["plan"] = new_plan
            self._customers[org_id]["mrr"] = new_mrr
            return True
        return False
    def remove(self, org_id: str) -> bool:
        if org_id in self._customers:
            del self._customers[org_id]
            return True
        return False
