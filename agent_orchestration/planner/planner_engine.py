"""Planner subsystem facade (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_events import (OrchestratorEvents,
                                                     OrchestratorEventType)
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import AgentTask
from agent_orchestration.orchestrator_registry import OrchestratorRegistry
from agent_orchestration.planner.dependency_mapper import DependencyMapper
from agent_orchestration.planner.resource_planner import ResourcePlanner
from agent_orchestration.planner.strategy_builder import StrategyBuilder
from agent_orchestration.planner.task_analyzer import TaskAnalyzer
from agent_orchestration.planner.task_breaker import TaskBreaker


class PlannerEngine:
    """Facade over request analysis, breaking and assignment."""

    def __init__(self, registry: OrchestratorRegistry | None = None,
                 events: OrchestratorEvents | None = None,
                 metrics: OrchestratorMetrics | None = None,
                 analyzer: TaskAnalyzer | None = None,
                 breaker: TaskBreaker | None = None,
                 mapper: DependencyMapper | None = None,
                 strategy: StrategyBuilder | None = None,
                 resources: ResourcePlanner | None = None) -> None:
        self.registry = registry or OrchestratorRegistry()
        self.events = events or OrchestratorEvents()
        self.metrics = metrics or OrchestratorMetrics()
        self.analyzer = analyzer or TaskAnalyzer()
        self.breaker = breaker or TaskBreaker()
        self.mapper = mapper or DependencyMapper()
        self.strategy = strategy or StrategyBuilder()
        self.resources = resources or ResourcePlanner()

    def plan(self, request: str, agents: list | None = None) -> list[AgentTask]:
        analysis = self.analyzer.analyze(request)
        tasks = self.breaker.break_down(request)
        self.mapper.link_sequential(tasks)
        for task in tasks:
            self.register_task(task)
            self.events.publish(OrchestratorEventType.TASK_PLANNED,
                                {"task_id": task.task_id, "title": task.title})
        self.metrics.increment("ao.plans")
        self.metrics.increment("ao.tasks_planned", len(tasks))
        if agents:
            self.resources.assign(tasks, agents)
        return tasks

    def register_task(self, task: AgentTask) -> None:
        self.registry.register_task(task)
        self.metrics.increment("ao.tasks")

    def get_task(self, task_id: str) -> AgentTask | None:
        return self.registry.get_task(task_id)

    def list_tasks(self) -> list[AgentTask]:
        return self.registry.list_tasks()

    def topological(self, tasks: list[AgentTask] | None = None) -> list[str]:
        return self.mapper.order(tasks or self.list_tasks())

    def stats(self) -> dict[str, Any]:
        return {
            "tasks": self.registry.count_tasks(),
            "plans": self.metrics.count("ao.plans"),
            "metrics": self.metrics.snapshot()["counters"],
        }
