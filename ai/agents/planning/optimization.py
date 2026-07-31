"""Planning optimization for task ordering and resource allocation."""
from __future__ import annotations

from typing import Any


class PlanningOptimizer:
    """Optimizes plans for minimal execution time and resource usage."""

    def __init__(self) -> None:
        self._optimization_count: int = 0

    def optimize(self, tasks: list[dict[str, Any]],
                 strategy: str = "time") -> list[dict[str, Any]]:
        self._optimization_count += 1
        if strategy == "time":
            return self._optimize_for_time(tasks)
        elif strategy == "resources":
            return self._optimize_for_resources(tasks)
        return tasks

    def _optimize_for_time(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        independent = [t for t in tasks if not t.get("dependencies")]
        dependent = [t for t in tasks if t.get("dependencies")]
        independent.sort(key=lambda t: t.get("priority", 5), reverse=True)
        dependent.sort(key=lambda t: len(t.get("dependencies", [])))
        return independent + dependent

    def _optimize_for_resources(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        effort_order = {"low": 1, "medium": 2, "high": 3}
        return sorted(
            tasks,
            key=lambda t: effort_order.get(t.get("estimated_effort", "medium"), 2),
        )

    def estimate_completion_time(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        effort_map = {"low": 5, "medium": 15, "high": 30}
        total_minutes = sum(
            effort_map.get(t.get("estimated_effort", "medium"), 15)
            for t in tasks
        )
        return {
            "total_tasks": len(tasks),
            "estimated_minutes": total_minutes,
            "estimated_hours": round(total_minutes / 60, 1),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"total_optimizations": self._optimization_count}
