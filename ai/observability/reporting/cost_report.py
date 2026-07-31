"""Cost report."""
from __future__ import annotations

import time
from typing import Any


class CostReport:
    def __init__(self) -> None:
        self._costs: dict[str, list[dict[str, Any]]] = {}
    def record_cost(self, service: str, amount: float, category: str = "general") -> None:
        self._costs.setdefault(service, []).append({"amount": amount, "category": category, "timestamp": time.time()})
    def get_total(self, service: str = "") -> float:
        if service:
            return sum(c["amount"] for c in self._costs.get(service, []))
        return sum(sum(c["amount"] for c in costs) for costs in self._costs.values())
    def get_by_category(self) -> dict[str, float]:
        categories: dict[str, float] = {}
        for costs in self._costs.values():
            for c in costs:
                cat = c.get("category", "general")
                categories[cat] = categories.get(cat, 0) + c["amount"]
        return categories
    def generate_report(self) -> dict[str, Any]:
        return {"total": self.get_total(), "by_category": self.get_by_category(), "services": list(self._costs.keys()), "timestamp": time.time()}
    def list_services(self) -> list[str]:
        return list(self._costs.keys())
    def get_service_costs(self, service: str) -> list[dict[str, Any]]:
        return self._costs.get(service, [])
    def clear(self, service: str = "") -> int:
        if service:
            n = len(self._costs.get(service, []))
            self._costs.pop(service, None)
            return n
        n = sum(len(v) for v in self._costs.values())
        self._costs.clear()
        return n
