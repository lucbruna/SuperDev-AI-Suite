"""Execution state tracking for workflows."""

from __future__ import annotations

import time
from typing import Any

from automation.automation_models import WorkflowStatus


class WorkflowState:
    """Mutable state of a single workflow run."""

    def __init__(self, workflow_id: str,
                 initial_vars: dict[str, Any] | None = None) -> None:
        self.workflow_id = workflow_id
        self.status = WorkflowStatus.PENDING
        self.current_step_id: str | None = None
        self.variables: dict[str, Any] = dict(initial_vars or {})
        self.step_results: dict[str, Any] = {}
        self.completed_steps: list[str] = []
        self.failed_steps: list[str] = []
        self.error: str | None = None
        self.started_at = time.time()
        self.finished_at: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "current_step_id": self.current_step_id,
            "variables": dict(self.variables),
            "step_results": dict(self.step_results),
            "completed_steps": list(self.completed_steps),
            "failed_steps": list(self.failed_steps),
            "error": self.error,
        }
