from __future__ import annotations

from typing import Any

from .planner_models import Plan, Task, TaskPriority


class PlannerStrategy:
    """Strategy patterns for plan creation."""

    @staticmethod
    def sequential(goal: str, steps: list[str]) -> Plan:
        plan = Plan(goal=goal)
        for i, step in enumerate(steps):
            plan.add_task(Task(
                name=step,
                description=f"Step {i + 1}: {step}",
                priority=TaskPriority.MEDIUM,
            ))
        return plan

    @staticmethod
    def parallel_groups(goal: str, groups: list[list[str]]) -> Plan:
        plan = Plan(goal=goal)
        for group in groups:
            for task_name in group:
                plan.add_task(Task(
                    name=task_name,
                    description=task_name,
                    tags=["parallelizable"],
                ))
        return plan

    @staticmethod
    def research_then_build(goal: str) -> Plan:
        plan = Plan(goal=goal)
        plan.add_task(Task(name="Research", description=f"Research: {goal}", priority=TaskPriority.HIGH))
        plan.add_task(Task(name="Design", description=f"Design: {goal}", priority=TaskPriority.HIGH))
        plan.add_task(Task(name="Implement", description=f"Implement: {goal}", priority=TaskPriority.HIGH))
        plan.add_task(Task(name="Test", description=f"Test: {goal}", priority=TaskPriority.MEDIUM))
        plan.add_task(Task(name="Deploy", description=f"Deploy: {goal}", priority=TaskPriority.MEDIUM))
        return plan
