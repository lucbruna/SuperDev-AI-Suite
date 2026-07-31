"""Resource optimizer."""
from __future__ import annotations
from typing import Any, Dict, List

class ResourceOptimizer:
    def __init__(self) -> None:
        self._resources: Dict[str, Dict[str, Any]] = {}
        self._allocations: List[Dict[str, Any]] = []
    def add_resource(self, name: str, capacity: float, cost_per_unit: float = 1.0) -> Dict[str, Any]:
        self._resources[name] = {"capacity": capacity, "available": capacity, "cost_per_unit": cost_per_unit}
        return {"name": name, "capacity": capacity}
    def allocate(self, resource_name: str, amount: float) -> Dict[str, Any]:
        if resource_name not in self._resources:
            return {"error": "not_found"}
        res = self._resources[resource_name]
        if amount > res["available"]:
            return {"error": "insufficient", "available": res["available"]}
        res["available"] -= amount
        cost = amount * res["cost_per_unit"]
        allocation = {"resource": resource_name, "amount": amount, "cost": cost}
        self._allocations.append(allocation)
        return allocation
    def optimize(self, demand: Dict[str, float], budget: float) -> Dict[str, Any]:
        allocations = {}
        total_cost = 0
        for resource, amount in demand.items():
            if resource in self._resources:
                res = self._resources[resource]
                alloc_amount = min(amount, res["available"])
                cost = alloc_amount * res["cost_per_unit"]
                if total_cost + cost <= budget:
                    allocations[resource] = {"amount": alloc_amount, "cost": cost}
                    total_cost += cost
        return {"allocations": allocations, "total_cost": total_cost, "budget": budget, "remaining": budget - total_cost}
    def get_resources(self) -> Dict[str, Any]:
        return dict(self._resources)
    def get_allocations(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._allocations[-limit:]
    def count(self) -> int:
        return len(self._resources)
