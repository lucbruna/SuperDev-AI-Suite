from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .planner_context import PlannerContext
from .planner_models import Plan, Task, TaskPriority, TaskStatus


class PlannerBuilder:
    """Builds plans from goals and context."""

    def build(self, context: PlannerContext) -> Plan:
        goal = context.get("goal", "Unnamed goal")
        plan = Plan(
            goal=goal,
            created_at=datetime.now(UTC),
            context=context.snapshot(),
        )
        tasks = self._decompose(goal, context)
        for task in tasks:
            plan.add_task(task)
        return plan

    def _decompose(self, goal: str, context: PlannerContext) -> list[Task]:
        """Decompose a goal into tasks."""
        return [
            Task(name=f"Analyze: {goal[:50]}", description=f"Analyze requirements for: {goal}", priority=TaskPriority.HIGH),
            Task(name=f"Plan: {goal[:50]}", description=f"Create execution plan for: {goal}", priority=TaskPriority.HIGH),
            Task(name=f"Execute: {goal[:50]}", description=f"Execute the plan for: {goal}", priority=TaskPriority.MEDIUM),
            Task(name=f"Verify: {goal[:50]}", description=f"Verify results for: {goal}", priority=TaskPriority.MEDIUM),
        ]

    def add_custom_task(self, plan: Plan, task: Task) -> Plan:
        plan.add_task(task)
        return plan
