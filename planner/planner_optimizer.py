from __future__ import annotations

from typing import Any

from .planner_models import Plan, Task


class PlannerOptimizer:
    """Optimizes plans for cost, duration, and resource usage."""

    def __init__(self):
        self.optimizations_applied: list[str] = []

    def optimize(self, plan: Plan) -> Plan:
        self._parallelize_tasks(plan)
        self._merge_redundant_tasks(plan)
        self._reorder_by_dependency(plan)
        self.optimizations_applied.append(f"Optimized plan '{plan.id}'")
        return plan

    def _parallelize_tasks(self, plan: Plan) -> None:
        tasks = plan.tasks
        independent: dict[str, list[Task]] = {}
        for task in tasks:
            key = getattr(task, "category", "general")
            if key not in independent:
                independent[key] = []
            independent[key].append(task)
        plan.tasks = []
        for category, cat_tasks in independent.items():
            if len(cat_tasks) > 1:
                for t in cat_tasks:
                    t.tags.append("parallelizable")
            plan.tasks.extend(cat_tasks)

    def _merge_redundant_tasks(self, plan: Plan) -> None:
        seen: set[str] = set()
        unique: list[Task] = []
        for task in plan.tasks:
            key = task.name.lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(task)
        plan.tasks = unique

    def _reorder_by_dependency(self, plan: Plan) -> None:
        plan.tasks.sort(key=lambda t: getattr(t, "priority", 0))
