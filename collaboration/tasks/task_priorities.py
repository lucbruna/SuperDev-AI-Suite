"""Task priority helpers."""

from __future__ import annotations

from collaboration.collaboration_models import TaskPriority

PRIORITY_ORDER = {
    TaskPriority.LOW: 0,
    TaskPriority.MEDIUM: 1,
    TaskPriority.HIGH: 2,
    TaskPriority.URGENT: 3,
}


def priority_rank(priority: TaskPriority) -> int:
    return PRIORITY_ORDER.get(priority, 1)


def priority_name(priority: TaskPriority) -> str:
    return priority.value


def prioritize(tasks: list, key=lambda t: t.priority) -> list:
    """Sorts tasks by priority descending (most urgent first)."""
    return sorted(tasks, key=lambda t: priority_rank(key(t)), reverse=True)
