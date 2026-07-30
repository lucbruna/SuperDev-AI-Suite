from __future__ import annotations

from typing import Any


class PlannerConstraints:
    """Constraint validation for planner tasks and plans."""

    def __init__(self):
        self._constraints: dict[str, Any] = {
            "max_tasks": 100,
            "max_depth": 10,
            "min_task_duration": 1.0,
            "max_task_duration": 3600.0,
        }

    def validate(self, plan: Any) -> list[str]:
        errors: list[str] = []
        tasks = getattr(plan, "tasks", [])
        if len(tasks) > self._constraints["max_tasks"]:
            errors.append(f"Task count {len(tasks)} exceeds max {self._constraints['max_tasks']}")
        for task in tasks:
            duration = getattr(task, "estimated_duration", 0)
            if duration < self._constraints["min_task_duration"]:
                errors.append(f"Task '{getattr(task, 'name', '')}' duration too short")
            if duration > self._constraints["max_task_duration"]:
                errors.append(f"Task '{getattr(task, 'name', '')}' duration too long")
        return errors

    def set(self, key: str, value: Any) -> None:
        self._constraints[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._constraints.get(key, default)
