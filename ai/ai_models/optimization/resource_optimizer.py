"""Resource optimization."""

from __future__ import annotations

from typing import Any


class ResourceOptimizer:
    def __init__(self) -> None:
        self._allocations: dict[str, dict[str, Any]] = {}
        self._history: list[dict[str, Any]] = []

    def allocate(self, resource: str, amount: float, unit: str = "units") -> dict[str, Any]:
        alloc = {"resource": resource, "amount": amount, "unit": unit}
        self._allocations[resource] = alloc
        return alloc

    def deallocate(self, resource: str) -> bool:
        if resource in self._allocations:
            del self._allocations[resource]
            return True
        return False

    def usage(self, resource: str) -> dict[str, Any]:
        alloc = self._allocations.get(resource, {})
        used = alloc.get("amount", 0) * 0.7
        return {
            "resource": resource,
            "allocated": alloc.get("amount", 0),
            "used": used,
            "available": alloc.get("amount", 0) - used,
        }

    def optimize(self, resource: str) -> dict[str, Any]:
        usage = self.usage(resource)
        if usage["available"] > usage["allocated"] * 0.5:
            suggested = usage["used"] * 1.2
            return {
                "resource": resource,
                "action": "reduce",
                "suggested": suggested,
                "savings": usage["allocated"] - suggested,
            }
        return {"resource": resource, "action": "maintain"}

    def list_resources(self) -> list[str]:
        return list(self._allocations.keys())

    def total_allocations(self) -> dict[str, float]:
        return {r: a["amount"] for r, a in self._allocations.items()}

    def count(self) -> int:
        return len(self._allocations)
