from __future__ import annotations

import json
from typing import Any

from .planner_models import Plan, Task


class PlannerSerialization:
    """Serialization for planner objects."""

    @staticmethod
    def plan_to_dict(plan: Plan) -> dict[str, Any]:
        return plan.model_dump()

    @staticmethod
    def plan_to_json(plan: Plan, indent: int = 2) -> str:
        return plan.model_dump_json(indent=indent)

    @staticmethod
    def task_to_dict(task: Task) -> dict[str, Any]:
        return task.model_dump()

    @staticmethod
    def task_to_json(task: Task, indent: int = 2) -> str:
        return task.model_dump_json(indent=indent)
