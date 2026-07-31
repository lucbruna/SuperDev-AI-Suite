"""Capacity planning for resource provisioning."""
from __future__ import annotations

from typing import Any


class CapacityPlanner:
    """Plans capacity requirements based on demand forecasting."""

    def __init__(self) -> None:
        self._utilization_target: float = 0.75
        self._safety_margin: float = 1.2

    def plan(self, demand: dict[str, Any]) -> dict[str, Any]:
        agents_needed = int(demand.get("expected_agents", 5))
        tasks_per_agent = int(demand.get("tasks_per_agent", 10))
        peak_multiplier = float(demand.get("peak_multiplier", 1.5))
        base_capacity = agents_needed * tasks_per_agent
        peak_capacity = int(base_capacity * peak_multiplier * self._safety_margin)
        recommended_agents = int(agents_needed * self._safety_margin / self._utilization_target)
        return {
            "base_capacity": base_capacity,
            "peak_capacity": peak_capacity,
            "recommended_agents": recommended_agents,
            "utilization_target": self._utilization_target,
            "safety_margin": self._safety_margin,
        }

    def set_utilization_target(self, target: float) -> None:
        self._utilization_target = min(max(target, 0.1), 1.0)

    def set_safety_margin(self, margin: float) -> None:
        self._safety_margin = max(margin, 1.0)
