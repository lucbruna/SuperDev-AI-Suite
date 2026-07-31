"""Orchestration engine: facade for the orchestration subsystem."""

from __future__ import annotations

from typing import Any, Callable

from automation.orchestration.orchestration_agent import OrchestrationAgent
from automation.orchestration.orchestration_coordinator import OrchestrationCoordinator
from automation.orchestration.orchestration_models import OrchestrationPlan


class OrchestrationEngine:
    """Plan, dispatch, and track multi-agent goals."""

    def __init__(self, coordinator: OrchestrationCoordinator | None = None) -> None:
        self.coordinator = coordinator or OrchestrationCoordinator()
        self.monitor = self.coordinator.monitor

    def register_agent(self, agent_id: str, role: str,
                       capabilities: list[str],
                       handler: Callable[[Any], Any] | None = None) -> OrchestrationAgent:
        agent = OrchestrationAgent(agent_id, role, capabilities, handler)
        self.coordinator.register_agent(agent)
        return agent

    def plan(self, goal: str, agent_ids: list[str] | None = None) -> OrchestrationPlan:
        return self.coordinator.plan(goal, agent_ids)

    def dispatch(self, plan_id: str) -> list[Any]:
        return self.coordinator.dispatch(plan_id)

    def execute_goal(self, goal: str,
                     agent_ids: list[str] | None = None) -> OrchestrationPlan:
        """Plan + dispatch in one call."""
        plan = self.coordinator.plan(goal, agent_ids)
        self.coordinator.dispatch(plan.plan_id)
        return plan

    def progress(self, plan_id: str) -> dict[str, Any]:
        return self.coordinator.progress(plan_id)

    def results(self, plan_id: str) -> dict[str, Any]:
        return self.coordinator.results(plan_id)

    def task_result(self, plan_id: str, task_id: str) -> Any:
        plan = self.coordinator.plans[plan_id]
        task = plan.task(task_id)
        return task.result if task is not None else None
