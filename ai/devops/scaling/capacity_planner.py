"""Capacity planner."""
from __future__ import annotations
from typing import Any, Dict, List

class CapacityPlanner:
    def __init__(self) -> None:
        self._plans: Dict[str, Dict[str, Any]] = {}
    def create_plan(self, name: str, current: Dict[str, int], projected: Dict[str, int]) -> Dict[str, Any]:
        plan = {"name": name, "current": current, "projected": projected, "gaps": {}}
        for resource in projected:
            current_val = current.get(resource, 0)
            projected_val = projected.get(resource, 0)
            plan["gaps"][resource] = projected_val - current_val
        self._plans[name] = plan
        return plan
    def get_plan(self, name: str) -> Dict[str, Any]:
        return self._plans.get(name, {"error": "not_found"})
    def list_plans(self) -> List[Dict[str, Any]]:
        return list(self._plans.values())
    def count(self) -> int:
        return len(self._plans)
