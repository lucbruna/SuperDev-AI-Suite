from __future__ import annotations

from typing import Any


class PlannerCostEstimator:
    """Estimates cost of plan execution."""

    COST_PER_TASK: float = 0.01
    COST_PER_MINUTE: float = 0.05

    def estimate(self, plan: Any) -> dict[str, float]:
        tasks = getattr(plan, "tasks", [])
        task_count = len(tasks)
        total_duration = sum(
            getattr(t, "estimated_duration", 60.0) for t in tasks
        )
        return {
            "task_cost": round(task_count * self.COST_PER_TASK, 4),
            "duration_cost": round((total_duration / 60.0) * self.COST_PER_MINUTE, 4),
            "total_estimated_cost": round(
                task_count * self.COST_PER_TASK + (total_duration / 60.0) * self.COST_PER_MINUTE, 4
            ),
            "estimated_duration_minutes": round(total_duration / 60.0, 2),
        }
