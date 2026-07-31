"""Capacity monitor."""

from __future__ import annotations

from typing import Any


class CapacityMonitor:
    def __init__(self) -> None:
        self._capacities: dict[str, dict[str, Any]] = {}

    def set_capacity(self, resource: str, total: float, unit: str = "units") -> dict[str, Any]:
        capacity = {"resource": resource, "total": total, "used": 0, "unit": unit, "utilization_pct": 0}
        self._capacities[resource] = capacity
        return capacity

    def update_usage(self, resource: str, used: float) -> bool:
        if resource not in self._capacities:
            return False
        self._capacities[resource]["used"] = used
        total = self._capacities[resource]["total"]
        self._capacities[resource]["utilization_pct"] = (used / total * 100) if total > 0 else 0
        return True

    def get_status(self, resource: str) -> dict[str, Any]:
        return self._capacities.get(resource, {"error": "not_found"})

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._capacities.values())

    def list_high_utilization(self, threshold: float = 80.0) -> list[dict[str, Any]]:
        return [c for c in self._capacities.values() if c["utilization_pct"] >= threshold]

    def count(self) -> int:
        return len(self._capacities)
