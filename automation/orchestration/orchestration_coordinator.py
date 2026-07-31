"""Coordinates agents, plans, and dispatches."""

from __future__ import annotations

from typing import Any, Callable

from automation.orchestration.orchestration_agent import OrchestrationAgent
from automation.orchestration.orchestration_dispatcher import OrchestrationDispatcher
from automation.orchestration.orchestration_models import OrchestrationPlan
from automation.orchestration.orchestration_monitor import OrchestrationMonitor
from automation.orchestration.orchestration_planner import OrchestrationPlanner


class OrchestrationCoordinator:
    """Holds agents and plans and drives execution."""

    def __init__(self, planner: OrchestrationPlanner | None = None,
                 dispatcher: OrchestrationDispatcher | None = None,
                 monitor: OrchestrationMonitor | None = None) -> None:
        self.monitor = monitor or OrchestrationMonitor()
        self.planner = planner or OrchestrationPlanner()
        self.dispatcher = dispatcher or OrchestrationDispatcher(self.monitor)
        self.agents: dict[str, OrchestrationAgent] = {}
        self.plans: dict[str, OrchestrationPlan] = {}

    def register_agent(self, agent: OrchestrationAgent) -> None:
        self.agents[agent.agent_id] = agent

    def agent(self, agent_id: str) -> OrchestrationAgent | None:
        return self.agents.get(agent_id)

    def plan(self, goal: str, agent_ids: list[str] | None = None) -> OrchestrationPlan:
        plan = self.planner.plan(goal, agent_ids)
        self.plans[plan.plan_id] = plan
        return plan

    def add_plan(self, plan: OrchestrationPlan) -> None:
        self.plans[plan.plan_id] = plan

    def dispatch(self, plan_id: str) -> list[Any]:
        plan = self.plans[plan_id]
        return self.dispatcher.dispatch(plan, list(self.agents.values()))

    def progress(self, plan_id: str) -> dict[str, Any]:
        return self.monitor.progress(self.plans[plan_id])

    def results(self, plan_id: str) -> dict[str, Any]:
        plan = self.plans[plan_id]
        return {t.task_id: t.result for t in plan.tasks
                if t.status.name == "COMPLETED"}
