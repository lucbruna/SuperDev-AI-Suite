"""Runtime state — lifecycle state machine for runtime sessions.

States follow a linear progression with explicit valid transitions:

    PENDING -> RUNNING -> SUCCEEDED
                       -> FAILED
                       -> CANCELLED

Any attempt to move through an invalid transition raises ``ValueError``
so callers (executor, API, cleanup) cannot corrupt session state.
"""
from __future__ import annotations
from enum import StrEnum
from typing import Any


class RuntimeState(StrEnum):
    """Valid session states (string values so snapshots serialize cleanly)."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @classmethod
    def terminal(cls) -> set[RuntimeState]:
        """States from which no further transition is allowed."""
        return {cls.SUCCEEDED, cls.FAILED, cls.CANCELLED}

    def can_transition_to(self, target: RuntimeState) -> bool:
        """Whether a session in this state may move to ``target``."""
        if self in self.terminal():
            return False
        allowed: dict[RuntimeState, set[RuntimeState]] = {
            self.PENDING: {self.RUNNING, self.CANCELLED},
            self.RUNNING: {self.SUCCEEDED, self.FAILED, self.CANCELLED},
        }
        return target in allowed.get(self, set())

    def transition(self, target: RuntimeState) -> None:
        if not self.can_transition_to(target):
            raise ValueError(f"invalid runtime state transition: {self.value} -> {target.value}")


def state_guard(state: RuntimeState, target: RuntimeState, *, label: str = "session") -> None:
    """Raise a descriptive error when a transition is not allowed."""
    state.transition(target)


def snapshot_of(state: RuntimeState, **extra: Any) -> dict[str, Any]:
    return {"state": state.value, **extra}


__all__ = ["RuntimeState", "snapshot_of", "state_guard"]
