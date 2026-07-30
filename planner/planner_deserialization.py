from __future__ import annotations

from typing import Any

from .planner_models import Plan, Task


class PlannerDeserialization:
    """Deserialization for planner objects."""

    @staticmethod
    def dict_to_plan(data: dict[str, Any]) -> Plan:
        tasks_data = data.pop("tasks", [])
        plan = Plan(**data)
        for task_data in tasks_data:
            plan.add_task(Task(**task_data))
        return plan

    @staticmethod
    def dict_to_task(data: dict[str, Any]) -> Task:
        return Task(**data)
