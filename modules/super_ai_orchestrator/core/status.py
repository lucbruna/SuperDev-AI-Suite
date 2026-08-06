"""Task lifecycle statuses."""
from __future__ import annotations

from enum import Enum

# Lifecycle (as driven by the kernel, decision engine, governance and
# the executor):
#
#   PENDING -- submitted, not yet decided
#   QUEUED -- decided, waiting in the kernel queue
#   WAITING_APPROVAL -- governance gate open
#   REJECTED -- gate denied
#   SCHEDULED -- selected by the scheduler for execution
#   RUNNING -- executor is working on it
#   PAUSED -- kernel-paused at a checkpoint (resumable)
#   COMPLETED -- executed successfully
#   FAILED -- execution failed
#   CANCELLED -- cancelled before completion
#   ROLLED_BACK -- failed and its mutations were rolled back


class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    WAITING_APPROVAL = "waiting_approval"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"

    # Statuses that are still "alive" (not terminal).
    @classmethod
    def terminal(cls) -> frozenset["TaskStatus"]:
        return frozenset(
            {
                cls.COMPLETED,
                cls.FAILED,
                cls.CANCELLED,
                cls.ROLLED_BACK,
                cls.REJECTED,
            }
        )

    @classmethod
    def alive(cls) -> frozenset["TaskStatus"]:
        return frozenset(s for s in cls if s not in cls.terminal())
