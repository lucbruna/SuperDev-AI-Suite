"""Planner — deterministic step plans.

For each task kind there is a fixed template of steps. The planner emits the
template steps (plus, for tasks with a ``scope`` payload, a scope-check
step) in a stable order. Plans are pure functions of the task.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from modules.super_ai_orchestrator.core.task import Task

# Kind -> ordered step templates. Each entry: (action, description).
_PLAN_TEMPLATES: dict[str, tuple[tuple[str, str], ...]] = {
    "analyze": (
        ("collect", "Gather structure and context for the target"),
        ("inspect", "Inspect the relevant code and metadata"),
        ("findings", "Produce deterministic findings"),
    ),
    "plan": (
        ("break_down", "Decompose the goal into units of work"),
        ("sequence", "Order units by dependency"),
        ("estimate", "Attach effort/risk markers to each unit"),
    ),
    "develop": (
        ("inspect", "Inspect the target area of the codebase"),
        ("implement", "Implement the requested change"),
        ("verify", "Verify the change with the configured checks"),
    ),
    "repair": (
        ("reproduce", "Reproduce the reported failure"),
        ("diagnose", "Identify the root cause"),
        ("fix", "Apply the minimal fix"),
        ("verify", "Verify the fix"),
    ),
    "evolve": (
        ("measure", "Measure the current state of the target"),
        ("propose", "Propose an evolution with expected impact"),
        ("apply", "Apply the approved evolution"),
        ("validate", "Validate outcomes and record metrics"),
    ),
    "review": (
        ("read_diff", "Read the change under review"),
        ("check_standards", "Check against the project standards"),
        ("report", "Produce a review report with severity findings"),
    ),
    "monitor": (
        ("check_health", "Check orchestrator and system health"),
        ("collect", "Collect deterministic metrics"),
        ("report", "Report the health snapshot"),
    ),
    "recover": (
        ("assess", "Assess the damage and affected tasks"),
        ("restore", "Restore from the latest checkpoint or rollback"),
        ("verify", "Verify recovery"),
    ),
    "document": (
        ("gather", "Gather the context to document"),
        ("draft", "Draft the document"),
        ("revise", "Revise for accuracy and consistency"),
    ),
    "deploy": (
        ("build", "Build the artifact"),
        ("stage", "Stage the artifact"),
        ("release", "Release to the target environment"),
    ),
    "workflow": (
        ("parse", "Parse the workflow definition"),
        ("order", "Order the workflow steps"),
        ("dispatch", "Dispatch each step as a sub-task"),
    ),
    "coordinate": (
        ("decompose", "Decompose the goal into sub-tasks"),
        ("assign", "Assign sub-tasks to capable agents"),
        ("reconcile", "Reconcile sub-task results"),
    ),
    "agent": (
        ("delegate", "Delegate the goal to the selected agent"),
        ("collect", "Collect the agent output"),
        ("reconcile", "Reconcile the output into a result"),
    ),
}


@dataclass(frozen=True, slots=True)
class PlanStep:
    """One step in a plan.

    Attributes:
        index: 1-based position in the plan.
        action: short verb identifier.
        description: what the step does.
    """

    index: int
    action: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Planner:
    """Produces deterministic plans for tasks."""

    def __init__(self, default_steps: int = 8) -> None:
        self.default_steps = default_steps

    def plan(self, task: Task, max_steps: int | None = None) -> tuple[PlanStep, ...]:
        """Build the ordered plan for a task.

        Unknown kinds get a generic fallback plan so the pipeline never
        breaks, and a scope-check step is appended when the payload carries
        a ``scope`` value.
        """
        template = _PLAN_TEMPLATES.get(
            task.kind,
            (("prepare", "Prepare the task"), ("execute", "Execute the task"), ("verify", "Verify the outcome")),
        )
        steps: list[PlanStep] = [
            PlanStep(index=i + 1, action=action, description=description)
            for i, (action, description) in enumerate(template)
        ]
        if task.payload.get("scope"):
            steps.append(
                PlanStep(index=len(steps) + 1, action="scope", description="Confirm the declared scope")
            )
        limit = max_steps if max_steps is not None else self.default_steps
        return tuple(steps[:limit])

    def summary(self, plan: tuple[PlanStep, ...]) -> str:
        return " -> ".join(step.action for step in plan)

    def to_dict(self, plan: tuple[PlanStep, ...]) -> list[dict[str, Any]]:
        return [step.to_dict() for step in plan]
