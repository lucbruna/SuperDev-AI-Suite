"""Cost report."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class CostReport:
    def __init__(self) -> None:
        self._costs: Dict[str, List[Dict[str, Any]]] = {}
    def record_cost(self, service: str, amount: float, category: str = "general") -> None:
        self._costs.setdefault(service, []).append({"amount": amount, "category": category, "timestamp": time.time()})
    def get_total(self, service: str = "") -> float:
        if service:
            return sum(c["amount"] for c in self._costs.get(service, []))
        return sum(sum(c["amount"] for c in costs) for costs in self._costs.values())
    def get_by_category(self) -> Dict[str, float]:
        categories: Dict[str, float] = {}
        for costs in self._costs.values():
            for c in costs:
                cat = c.get("category", "general")
                categories[cat] = categories.get(cat, 0) + c["amount"]
        return categories
    def generate_report(self) -> Dict[str, Any]:
        return {"total": self.get_total(), "by_category": self.get_by_category(), "services": list(self._costs.keys()), "timestamp": time.time()}
    def list_services(self) -> List[str]:
        return list(self._costs.keys())
    def get_service_costs(self, service: str) -> List[Dict[str, Any]]:
        return self._costs.get(service, [])
    def clear(self, service: str = "") -> int:
        if service:
            n = len(self._costs.get(service, []))
            self._costs.pop(service, None)
            return n
        n = sum(len(v) for v in self._costs.values())
        self._costs.clear()
        return n
