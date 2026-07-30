from __future__ import annotations

from typing import Any

from .planner import Planner
from .planner_models import Plan, PlannerConfig, Task, TaskDependency


class PlannerFactory:
    """Factory for creating planner instances and plans."""

    @staticmethod
    def create_planner(config: PlannerConfig | None = None) -> Planner:
        return Planner(config)

    @staticmethod
    def create_plan(goal: str, **kwargs: Any) -> Plan:
        return Plan(goal=goal, **kwargs)

    @staticmethod
    def create_task(name: str, **kwargs: Any) -> Task:
        return Task(name=name, **kwargs)

    @staticmethod
    def create_dependency(from_task: str, to_task: str, **kwargs: Any) -> TaskDependency:
        return TaskDependency(from_task=from_task, to_task=to_task, **kwargs)

    @staticmethod
    def create_config(**kwargs: Any) -> PlannerConfig:
        return PlannerConfig(**kwargs)
