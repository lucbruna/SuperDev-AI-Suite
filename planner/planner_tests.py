from __future__ import annotations

from typing import Any

from .planner import Planner
from .planner_models import Plan, PlannerConfig, Task, TaskPriority


class PlannerTests:
    """Built-in tests for the planner module."""

    @staticmethod
    def test_create_plan() -> dict[str, Any]:
        planner = Planner()
        plan = Plan(
            goal="Test goal",
            tasks=[
                Task(name="Task 1", priority=TaskPriority.HIGH),
                Task(name="Task 2", priority=TaskPriority.MEDIUM),
            ],
        )
        return {
            "test": "create_plan",
            "passed": plan is not None and len(plan.tasks) == 2,
            "plan_id": plan.id,
        }

    @staticmethod
    def test_config_defaults() -> dict[str, Any]:
        config = PlannerConfig()
        return {
            "test": "config_defaults",
            "passed": config.max_tasks_per_plan == 50,
        }

    @staticmethod
    def run_all() -> list[dict[str, Any]]:
        return [
            PlannerTests.test_create_plan(),
            PlannerTests.test_config_defaults(),
        ]
