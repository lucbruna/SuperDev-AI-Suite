"""Planner: facade that turns goals into executable, scheduled plans."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from aios.planning.decomposer import Decomposer
from aios.planning.dependency_graph import DependencyGraph
from aios.planning.plan_optimizer import PlanOptimizer
from aios.planning.resource_allocator import ResourceAllocator
from aios.planning.task_builder import Task, TaskBuilder
from aios.planning.time_scheduler import TimeScheduler
from aios.planning.workflow_planner import WorkflowPlan, WorkflowPlanner

PLAN_STATUSES = ("draft", "active", "completed", "cancelled", "failed")


@dataclass
class Plan:
    plan_id: str
    goal: str
    status: str = "draft"
    tasks: list[Task] = field(default_factory=list)
    workflow: Optional[WorkflowPlan] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def task_by_id(self, task_id: str) -> Optional[Task]:
        return next((t for t in self.tasks if t.task_id == task_id), None)


class Planner:
    """Composes decomposition, task building, graph, scheduling and optimization."""

    def __init__(self, planner_id: str | None = None) -> None:
        self.planner_id = planner_id or f"planner-{uuid.uuid4().hex[:8]}"
        self.decomposer = Decomposer()
        self.task_builder = TaskBuilder()
        self.workflow_planner = WorkflowPlanner()
        self.resources = ResourceAllocator()
        self.scheduler = TimeScheduler()
        self.optimizer = PlanOptimizer()
        self._plans: dict[str, Plan] = {}

    def create_plan(
        self,
        goal: str,
        strategy: str = "hierarchical",
        subgoals: list[str] | None = None,
        duration: float = 1.0,
        optimize: bool = True,
        schedule: bool = True,
        t0: float = 0.0,
    ) -> Plan:
        specs = self.decomposer.decompose(goal, strategy=strategy, subgoals=subgoals, duration=duration)
        tasks = self.task_builder.build_many(specs)

        plan_id = f"plan-{len(self._plans) + 1}"
        plan = Plan(plan_id=plan_id, goal=str(goal), tasks=tasks)

        graph = DependencyGraph()
        for task in tasks:
            graph.add_node(task.task_id, name=task.name, duration=task.estimated_duration)
        for task in tasks:
            for dep in task.depends_on:
                graph.add_edge(task.task_id, dep)

        plan.workflow = self.workflow_planner.plan(tasks, plan_id=f"workflow-{plan_id}", graph=graph)
        durations = {t.task_id: t.estimated_duration for t in tasks}

        if optimize:
            report = self.optimizer.optimize(plan.workflow, durations)
            plan.metadata["optimization"] = report.to_dict()
        if schedule:
            entries = self.scheduler.schedule(plan.workflow.order, plan.workflow.dependencies, durations, t0=t0)
            for task_id, entry in entries.items():
                task = plan.task_by_id(task_id)
                if task is not None:
                    task.start_time = entry.start
                    task.end_time = entry.end
            plan.metadata["schedule"] = {task_id: entry.to_dict() for task_id, entry in sorted(entries.items())}

        plan.status = "active"
        plan.updated_at = time.time()
        self._plans[plan_id] = plan
        return plan

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        return self._plans.get(plan_id)

    def list_plans(self) -> list[Plan]:
        return [self._plans[plan_id] for plan_id in sorted(self._plans)]

    def set_plan_status(self, plan_id: str, status: str) -> Optional[Plan]:
        if status not in PLAN_STATUSES:
            raise ValueError(f"invalid plan status {status!r}; expected one of {PLAN_STATUSES}")
        plan = self._plans.get(plan_id)
        if plan is None:
            return None
        plan.status = status
        plan.updated_at = time.time()
        return plan

    def cancel_plan(self, plan_id: str) -> Optional[Plan]:
        return self.set_plan_status(plan_id, "cancelled")
