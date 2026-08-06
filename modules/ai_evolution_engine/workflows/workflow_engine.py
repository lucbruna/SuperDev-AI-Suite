"""Workflow definitions: deterministic pipeline orchestrations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class WorkflowStep:
    """One named step in a workflow."""

    name: str
    fn: Callable[[EvolutionContext], object] | None = None

    def run(self, ctx: EvolutionContext) -> object:
        if self.fn is None:
            return None
        return self.fn(ctx)


@dataclass(slots=True)
class Workflow:
    """A named sequence of steps executed in order."""

    name: str
    steps: list[WorkflowStep] = field(default_factory=list)

    def run(self, ctx: EvolutionContext) -> list[object]:
        outputs: list[object] = []
        for step in self.steps:
            outputs.append(step.run(ctx))
        return outputs


STANDARD_WORKFLOW = Workflow(
    name="standard",
    steps=[
        WorkflowStep("analyze"),
        WorkflowStep("recommend"),
        WorkflowStep("forecast"),
        WorkflowStep("govern"),
        WorkflowStep("plan"),
        WorkflowStep("report"),
    ],
)
