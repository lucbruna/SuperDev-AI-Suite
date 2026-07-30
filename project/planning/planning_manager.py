from __future__ import annotations

import logging
import uuid
from typing import Any


class Plan:
    """Represents a project plan."""

    def __init__(self, name: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.project_id = project_id
        self.phases: list[dict[str, Any]] = []
        self.status: str = "draft"


class PlanningManager:
    """Manages project planning."""

    def __init__(self) -> None:
        self._plans: dict[str, Plan] = {}
        self._log = logging.getLogger("superdev.project.planning")

    def create_plan(self, name: str, project_id: str) -> Plan:
        plan = Plan(name=name, project_id=project_id)
        self._plans[plan.id] = plan
        self._log.info("Created plan %s", plan.id)
        return plan

    def get_plan(self, plan_id: str) -> Plan | None:
        return self._plans.get(plan_id)

    def add_phase(self, plan_id: str, phase: dict[str, Any]) -> None:
        plan = self._plans.get(plan_id)
        if plan:
            plan.phases.append(phase)

    def list_plans(self, project_id: str) -> list[Plan]:
        return [p for p in self._plans.values() if p.project_id == project_id]
