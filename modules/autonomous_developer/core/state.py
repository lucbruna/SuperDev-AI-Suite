"""Developer state — lifecycle state machine for the autonomous flow.

Tracks the state of a task run (idle → planning → implementing → testing →
reviewing → ready), records transitions and captures the last error with
context.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DeveloperState(str, Enum):
    """Lifecycle states of an autonomous developer run."""

    UNINITIALIZED = "uninitialized"
    IDLE = "idle"
    PLANNING = "planning"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    REVIEWING = "reviewing"
    MERGING = "merging"
    READY = "ready"
    ERROR = "error"

    @property
    def terminal(self) -> bool:
        return self in {DeveloperState.READY, DeveloperState.ERROR}


@dataclass(slots=True)
class StateTransition:
    """One recorded state transition."""

    from_state: str
    to_state: str
    timestamp: float = field(default_factory=time.time)
    context: str = ""


class DeveloperStateTracker:
    """Thread-safe-ish state tracker with transition history."""

    def __init__(self) -> None:
        self._state = DeveloperState.UNINITIALIZED
        self._transitions: list[StateTransition] = []
        self._last_error: str = ""
        self._last_error_context: dict[str, Any] = {}
        self._started_at: float | None = None
        self._finished_at: float | None = None

    @property
    def state(self) -> DeveloperState:
        return self._state

    @property
    def last_error(self) -> str:
        return self._last_error

    @property
    def last_error_context(self) -> dict[str, Any]:
        return dict(self._last_error_context)

    @property
    def started_at(self) -> float | None:
        return self._started_at

    @property
    def finished_at(self) -> float | None:
        return self._finished_at

    @property
    def elapsed_seconds(self) -> float:
        if self._started_at is None:
            return 0.0
        end = self._finished_at or time.time()
        return round(end - self._started_at, 3)

    def set_state(self, new_state: DeveloperState, context: str = "") -> None:
        """Transition to ``new_state`` and record the transition."""
        previous = self._state
        if previous != new_state:
            self._transitions.append(
                StateTransition(from_state=previous.value, to_state=new_state.value, context=context)
            )
            if self._started_at is None and new_state not in {
                DeveloperState.IDLE,
                DeveloperState.UNINITIALIZED,
            }:
                self._started_at = time.time()
            if new_state.terminal:
                self._finished_at = time.time()
            if new_state != DeveloperState.ERROR:
                self._last_error = ""
                self._last_error_context = {}
        self._state = new_state

    def mark_error(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Record an error and move to the ERROR state."""
        self._last_error = message
        self._last_error_context = context or {}
        self.set_state(DeveloperState.ERROR, context="error")

    def transitions(self, limit: int = 20) -> list[StateTransition]:
        return self._transitions[-limit:]

    def reset(self) -> None:
        self._state = DeveloperState.IDLE
        self._transitions.clear()
        self._last_error = ""
        self._last_error_context = {}
        self._started_at = None
        self._finished_at = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self._state.value,
            "elapsed_seconds": self.elapsed_seconds,
            "last_error": self._last_error,
            "last_error_context": self._last_error_context,
            "transition_count": len(self._transitions),
            "last_transitions": [
                {"from": t.from_state, "to": t.to_state, "context": t.context}
                for t in self.transitions(5)
            ],
        }
