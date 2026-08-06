"""OrchestrationContext — the state bag attached to a running task."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from modules.super_ai_orchestrator.core.task import Task


@dataclass(slots=True)
class OrchestrationContext:
    """Everything an executor may need while running a task.

    Attributes:
        task: the task being executed.
        decision: the decision record (owner, llm, requires, rules used).
        plan: ordered step plan (list of step dicts) from the planner.
        variables: free-form state shared between steps.
        checkpoint: persisted resume state, managed by the kernel.
    """

    task: Task
    decision: dict[str, Any] | None = None
    plan: tuple[dict[str, Any], ...] = ()
    variables: dict[str, Any] = field(default_factory=dict)
    checkpoint: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task.to_dict(),
            "decision": self.decision,
            "plan": list(self.plan),
            "variables": self.variables,
            "checkpoint": self.checkpoint,
        }

    def snapshot(self) -> dict[str, Any]:
        """A compact snapshot used for checkpoints."""
        return {
            "variables": self.variables,
            "checkpoint": self.checkpoint,
            "plan": list(self.plan),
            "decision": self.decision,
        }

    def restore(self, snapshot: dict[str, Any]) -> None:
        """Restore state from a checkpoint snapshot."""
        self.variables = snapshot.get("variables", {})
        self.checkpoint = snapshot.get("checkpoint")
        self.plan = tuple(snapshot.get("plan", ()))
        self.decision = snapshot.get("decision")
