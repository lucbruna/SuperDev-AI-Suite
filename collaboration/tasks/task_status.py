"""Task status transitions."""

from __future__ import annotations

from collaboration.collaboration_models import TaskStatus

ALLOWED_TRANSITIONS: dict[TaskStatus, tuple[TaskStatus, ...]] = {
    TaskStatus.TODO: (TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED,
                      TaskStatus.DONE),
    TaskStatus.IN_PROGRESS: (TaskStatus.IN_REVIEW, TaskStatus.BLOCKED,
                             TaskStatus.DONE),
    TaskStatus.IN_REVIEW: (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
    TaskStatus.BLOCKED: (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    TaskStatus.DONE: (TaskStatus.IN_PROGRESS,),
}


def can_transition(current: TaskStatus, next_status: TaskStatus) -> bool:
    return next_status in ALLOWED_TRANSITIONS.get(current, ())


def transition(current: TaskStatus, next_status: TaskStatus) -> TaskStatus:
    """Returns next_status if allowed, otherwise the current status."""
    if can_transition(current, next_status):
        return next_status
    return current


def describe(current: TaskStatus) -> list[str]:
    return [s.value for s in ALLOWED_TRANSITIONS.get(current, ())]
