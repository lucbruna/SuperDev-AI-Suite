from __future__ import annotations

from typing import Any

from .worker_state import WorkerState


class WorkerHealth:
    """Monitors worker health status."""

    def __init__(self) -> None:
        self._states: dict[str, WorkerState] = {}
        self._errors: dict[str, str] = {}

    def report(self, worker_id: str, state: WorkerState, error: str | None = None) -> None:
        self._states[worker_id] = state
        if error:
            self._errors[worker_id] = error

    def is_healthy(self, worker_id: str) -> bool:
        return self._states.get(worker_id, WorkerState.IDLE) not in (
            WorkerState.ERROR, WorkerState.STOPPED
        )

    def summary(self) -> dict[str, Any]:
        return {
            "total": len(self._states),
            "healthy": sum(1 for w in self._states if self.is_healthy(w)),
            "errors": dict(self._errors),
        }
