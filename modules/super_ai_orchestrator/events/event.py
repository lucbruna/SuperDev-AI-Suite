"""Event value object and event type constants."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

# Orchestrator lifecycle.
ORCHESTRATOR_STARTED = "orchestrator.started"
ORCHESTRATOR_STOPPED = "orchestrator.stopped"

# Task lifecycle.
TASK_SUBMITTED = "task.submitted"
TASK_DECIDED = "task.decided"
TASK_QUEUED = "task.queued"
TASK_WAITING_APPROVAL = "task.waiting_approval"
TASK_APPROVED = "task.approved"
TASK_REJECTED = "task.rejected"
TASK_SCHEDULED = "task.scheduled"
TASK_STARTED = "task.started"
TASK_CHECKPOINTED = "task.checkpointed"
TASK_PAUSED = "task.paused"
TASK_RESUMED = "task.resumed"
TASK_COMPLETED = "task.completed"
TASK_FAILED = "task.failed"
TASK_CANCELLED = "task.cancelled"
TASK_ROLLED_BACK = "task.rolled_back"

# Decision.
DECISION_MADE = "decision.made"

# Kernel.
KERNEL_QUEUE_FULL = "kernel.queue_full"
KERNEL_DEDUPED = "kernel.deduped"


def event_types() -> tuple[str, ...]:
    return tuple(
        sorted(
            name
            for name, value in globals().items()
            if name.isupper() and isinstance(value, str) and value.startswith(("orchestrator.", "task.", "decision.", "kernel."))
        )
    )


@dataclass(frozen=True, slots=True)
class Event:
    """An immutable, deterministically ordered event.

    Attributes:
        type: one of the event type constants above.
        payload: structured data attached to the event.
        seq: monotonic sequence assigned by the bus at publish time.
    """

    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    seq: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
