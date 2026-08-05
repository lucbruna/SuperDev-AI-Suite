"""WorkflowPlanner: builds an executable workflow plan from tasks over a DAG."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from aios.planning.dependency_graph import DependencyGraph
from aios.planning.task_builder import Task


@dataclass
class WorkflowStep:
    task_id: str
    order: int
    level: int
    status: str = "pending"


@dataclass
class WorkflowPlan:
    plan_id: str
    steps: list[WorkflowStep] = field(default_factory=list)
    order: list[str] = field(default_factory=list)
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    critical_path: list[str] = field(default_factory=list)
    total_duration: float = 0.0
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def next_ready(self, completed: set[str] | None = None) -> list[str]:
        """Task ids whose dependencies are all completed, in workflow order."""
        done = set(completed or ())
        return [
            tid for tid in self.order
            if tid not in done and all(dep in done for dep in self.dependencies.get(tid, []))
        ]


class WorkflowPlanner:
    """Turns a list of tasks into a deterministic workflow plan.

    Use a fresh ``DependencyGraph`` per plan to avoid stale nodes from
    previous plans when the planner is reused.
    """

    def __init__(self, graph: DependencyGraph | None = None) -> None:
        self.graph = graph if graph is not None else DependencyGraph()

    def plan(
        self,
        tasks: list[Task],
        plan_id: str | None = None,
        graph: DependencyGraph | None = None,
    ) -> WorkflowPlan:
        graph = graph if graph is not None else self.graph
        for task in tasks:
            graph.add_node(task.task_id, name=task.name, duration=task.estimated_duration)
        for task in tasks:
            for dep in task.depends_on:
                graph.add_edge(task.task_id, dep)

        plan_id = plan_id or f"workflow-{uuid.uuid4().hex[:8]}"
        order = graph.topological_sort()
        path, total = graph.critical_path()
        dependencies = {tid: graph.dependencies_of(tid) for tid in order}
        steps = [
            WorkflowStep(task_id=tid, order=idx, level=graph.level_of(tid))
            for idx, tid in enumerate(order)
        ]
        return WorkflowPlan(
            plan_id=plan_id,
            steps=steps,
            order=order,
            dependencies=dependencies,
            critical_path=path,
            total_duration=total,
        )
