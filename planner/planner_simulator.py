from __future__ import annotations

import random
from typing import Any


class PlannerSimulator:
    """Simulates plan execution for testing and estimation."""

    def simulate(self, plan: Any, fast_forward: bool = True) -> dict[str, Any]:
        tasks = getattr(plan, "tasks", [])
        results = []
        total_duration = 0.0

        for task in tasks:
            duration = getattr(task, "estimated_duration", random.uniform(10, 120))
            success = random.random() > 0.1  # 90% success rate
            total_duration += duration if fast_forward else duration * 2
            results.append({
                "task": getattr(task, "name", "unknown"),
                "duration": round(duration, 2),
                "success": success,
                "error": None if success else "Simulated failure",
            })

        return {
            "plan_id": getattr(plan, "id", "unknown"),
            "simulated": True,
            "total_duration": round(total_duration, 2),
            "tasks_count": len(tasks),
            "success_count": sum(1 for r in results if r["success"]),
            "failure_count": sum(1 for r in results if not r["success"]),
            "results": results,
        }
