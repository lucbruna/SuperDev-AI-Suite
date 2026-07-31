from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowStepState:
    """State of a single workflow step."""

    step_id: str
    name: str
    status: str = "pending"  # pending | running | completed | failed | skipped
    result: Any = None
    started_at: float | None = None
    finished_at: float | None = None


@dataclass
class WorkflowState:
    """State of a workflow execution."""

    workflow_id: str
    name: str = ""
    status: str = "pending"  # pending | running | completed | failed | cancelled
    steps: list[WorkflowStepState] = field(default_factory=list)
    error: str | None = None

    def start(self) -> None:
        self.status = "running"

    def update_step(self, step_id: str, **values: Any) -> None:
        for step in self.steps:
            if step.step_id == step_id:
                for key, value in values.items():
                    setattr(step, key, value)
                return
        raise KeyError(f"unknown workflow step: {step_id}")

    def complete(self) -> None:
        self.status = "completed"

    def fail(self, error: str) -> None:
        self.status = "failed"
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status,
            "steps": [vars(s) for s in self.steps],
            "error": self.error,
        }
