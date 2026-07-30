from __future__ import annotations

import time
from typing import Any

from .workflow_models import StepStatus


class WorkflowStateManager:
    """Manages execution state for a workflow."""

    def __init__(self, workflow_id: str) -> None:
        self._workflow_id = workflow_id
        self._current_step: str | None = None
        self._completed: list[str] = []
        self._failed: list[str] = []
        self._data: dict[str, Any] = {}
        self._errors: list[str] = []

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    @property
    def current_step(self) -> str | None:
        return self._current_step

    def set_current_step(self, step_id: str) -> None:
        self._current_step = step_id

    def complete_step(self, step_id: str) -> None:
        if step_id not in self._completed:
            self._completed.append(step_id)
        if self._current_step == step_id:
            self._current_step = None

    def fail_step(self, step_id: str, error: str) -> None:
        if step_id not in self._failed:
            self._failed.append(step_id)
        self._errors.append(error)

    def set_data(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def is_step_completed(self, step_id: str) -> bool:
        return step_id in self._completed

    def is_step_failed(self, step_id: str) -> bool:
        return step_id in self._failed

    def snapshot(self) -> dict[str, Any]:
        return {
            "workflow_id": self._workflow_id,
            "current_step": self._current_step,
            "completed": list(self._completed),
            "failed": list(self._failed),
            "data": dict(self._data),
            "errors": list(self._errors),
        }
