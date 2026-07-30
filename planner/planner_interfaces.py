from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .planner_models import Plan, PlannerConfig


class IPlanner(ABC):
    """Public interface for the Planner."""

    @abstractmethod
    async def create_plan(self, goal: str, **kwargs: Any) -> Plan: ...

    @abstractmethod
    async def execute_plan(self, plan_id: str) -> dict[str, Any]: ...

    @abstractmethod
    def get_plan(self, plan_id: str) -> Plan | None: ...

    @abstractmethod
    def list_plans(self) -> list[Plan]: ...


class IPlannerService(ABC):
    @abstractmethod
    def validate_plan(self, plan: Plan) -> dict[str, Any]: ...

    @abstractmethod
    def estimate_duration(self, plan: Plan) -> float: ...
