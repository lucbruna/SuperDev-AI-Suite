"""Cost optimizer."""
from __future__ import annotations

from typing import Any


class CostOptimizer:
    def __init__(self) -> None:
        self._costs: dict[str, float] = {}
        self._optimizations: list[dict[str, Any]] = []
    def add_cost(self, name: str, amount: float, category: str = "general") -> dict[str, Any]:
        self._costs[name] = amount
        return {"name": name, "amount": amount, "category": category}
    def get_total(self) -> float:
        return sum(self._costs.values())
    def optimize(self, budget: float, priorities: dict[str, float] = None) -> dict[str, Any]:
        priorities = priorities or {k: 1.0 for k in self._costs}
        total = self.get_total()
        if total <= budget:
            return {"status": "within_budget", "total": total, "budget": budget, "savings": 0}
        reduction_needed = total - budget
        sorted_costs = sorted(self._costs.items(), key=lambda x: priorities.get(x[0], 1.0), reverse=True)
        allocations = {}
        remaining = budget
        for name, cost in sorted_costs:
            allocated = min(cost, remaining)
            allocations[name] = allocated
            remaining -= allocated
            if remaining <= 0:
                break
        result = {"status": "optimized", "total": sum(allocations.values()), "budget": budget, "reduction": reduction_needed, "allocations": allocations}
        self._optimizations.append(result)
        return result
    def get_optimizations(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._optimizations[-limit:]
    def list_costs(self) -> dict[str, float]:
        return dict(self._costs)
    def count(self) -> int:
        return len(self._costs)
