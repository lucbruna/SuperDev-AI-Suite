"""Task planner — ordering, estimation and phase assignment.

Operates on :class:`TaskPlan` objects produced by the project planner:
orders tasks so dependencies run first (Kahn, stable), detects dependency
cycles, estimates effort and assigns flow phases.
"""
from __future__ import annotations

from typing import Any

from modules.autonomous_developer.config.constants import (
    OP_TEST,
    PHASE_IMPLEMENT,
    PHASE_TEST,
    RISK_HIGH,
    RISK_CRITICAL,
)
from modules.autonomous_developer.config.planner_config import PlannerConfig
from modules.autonomous_developer.core.models import Task, TaskPlan

_RISK_ESTIMATE_MULTIPLIERS = {RISK_HIGH: 1.5, RISK_CRITICAL: 2.0}


class TaskPlanner:
    """Orders tasks topologically and estimates effort."""

    def __init__(self, config: PlannerConfig | None = None) -> None:
        self.config = config or PlannerConfig()

    def order_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered so dependencies come first (Kahn, stable).

        Tasks involved in dependency cycles are appended in their original
        relative order after the acyclic remainder. Unknown dependency ids
        (not present in ``tasks``) never block scheduling.
        """
        remaining = {task.task_id for task in tasks}
        ordered: list[Task] = []
        while remaining:
            ready = [
                task
                for task in tasks
                if task.task_id in remaining
                and not any(dep in remaining for dep in task.depends_on)
            ]
            if not ready:
                # Dependency cycle: keep the remainder in original order.
                ordered.extend(task for task in tasks if task.task_id in remaining)
                break
            for task in ready:
                ordered.append(task)
                remaining.discard(task.task_id)
        return ordered

    def detect_cycles(self, tasks: list[Task]) -> list[list[str]]:
        """Return dependency cycles as lists of task ids (deduplicated)."""
        by_id = {task.task_id: task for task in tasks}
        white, gray, black = 0, 1, 2
        color = {task_id: white for task_id in by_id}
        stack: list[str] = []
        cycles: list[list[str]] = []
        seen_keys: set[tuple[str, ...]] = set()

        def visit(node: str) -> None:
            color[node] = gray
            stack.append(node)
            for dep in by_id[node].depends_on:
                if dep not in by_id:
                    continue
                if color[dep] == gray:
                    index = stack.index(dep)
                    cycle = stack[index:] + [dep]
                    key = tuple(sorted(cycle))
                    if key not in seen_keys:
                        seen_keys.add(key)
                        cycles.append(cycle)
                elif color[dep] == white:
                    visit(dep)
            stack.pop()
            color[node] = black

        for task in tasks:
            if color[task.task_id] == white:
                visit(task.task_id)
        return cycles

    def estimate_hours(self, task: Task) -> float:
        """Heuristic estimate: base + description size, scaled by risk."""
        hours = 0.5 + (len(f"{task.title} {task.description}") / 400.0)
        multiplier = _RISK_ESTIMATE_MULTIPLIERS.get(task.risk, 1.0)
        hours *= multiplier
        return round(min(hours, self.config.max_estimation_hours), 2)

    def assign_phase(self, task: Task) -> str:
        """Return the flow phase a task belongs to (keeps explicit phase)."""
        if task.phase:
            return task.phase
        for change in task.files:
            if change.operation == OP_TEST:
                return PHASE_TEST
        return PHASE_IMPLEMENT

    def analyze(self, plan: TaskPlan) -> dict[str, Any]:
        """Full analysis: ordering, cycles and effort estimate."""
        ordered = self.order_tasks(plan.tasks)
        total = sum(self.estimate_hours(task) for task in plan.tasks)
        return {
            "plan_id": plan.plan_id,
            "task_count": len(plan.tasks),
            "ordered": [task.task_id for task in ordered],
            "cycles": self.detect_cycles(plan.tasks),
            "estimated_hours": round(total, 2),
        }
