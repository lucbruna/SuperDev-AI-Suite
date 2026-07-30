from __future__ import annotations

from typing import Any


class ExecutionState:
    """Tracks the current state of a workflow execution."""

    def __init__(self) -> None:
        self._current_step: str | None = None
        self._completed: list[str] = []
        self._failed: list[str] = []
        self._data: dict[str, Any] = {}
        self._errors: list[str] = []

    @property
    def current_step(self) -> str | None:
        return self._current_step

    def start_step(self, step_id: str) -> None:
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

    def is_completed(self, step_id: str) -> bool:
        return step_id in self._completed

    def is_failed(self, step_id: str) -> bool:
        return step_id in self._failed

    def snapshot(self) -> dict[str, Any]:
        return {
            "current_step": self._current_step,
            "completed": list(self._completed),
            "failed": list(self._failed),
            "errors": list(self._errors),
        }
