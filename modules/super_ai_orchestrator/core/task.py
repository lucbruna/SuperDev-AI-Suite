"""The Task — the unit of orchestration.

A task is what the orchestrator decides about, schedules and executes.
Ordering is deterministic: the kernel assigns a monotonic ``seq`` at submit
time and the priority queue always pops the highest-priority oldest task.
No timestamps are used for decision-making; ``created_at`` is display-only
and stamped by outer layers (API/CLI) if desired.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any

from modules.super_ai_orchestrator.core.status import TaskStatus


@dataclass(slots=True)
class Task:
    """A unit of work submitted to the orchestrator.

    Attributes:
        kind: task kind, e.g. ``develop``, ``repair``, ``evolve``.
        title: human-readable title.
        payload: arbitrary structured input for the executor.
        priority: urgency 1..10 (10 = most urgent).
        owner: agent name chosen by the Decision Engine (e.g. ``developer``).
        llm: provider name chosen by the Decision Engine (e.g. ``claude``).
        requires: tool names required by the task (e.g. ``git``, ``rag``).
        seq: monotonic order assigned by the kernel (deterministic tiebreak).
        status: current lifecycle status.
        reason: rejection or error reason.
        result: structured result produced by the executor.
        error: error message if execution failed.
        attempts: number of execution attempts made.
        checkpoint: persisted state for resumption.
        created_at: display-only timestamp stamped by outer layers.
    """

    kind: str
    title: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    owner: str | None = None
    llm: str | None = None
    requires: tuple[str, ...] = ()
    seq: int = 0
    status: TaskStatus = TaskStatus.PENDING
    reason: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    attempts: int = 0
    checkpoint: dict[str, Any] | None = None
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["requires"] = list(self.requires)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        known = {f.name for f in fields(cls)}
        payload = {k: v for k, v in data.items() if k in known}
        payload["status"] = TaskStatus(payload.get("status", TaskStatus.PENDING))
        payload["requires"] = tuple(payload.get("requires", ()))
        return cls(**payload)

    def key(self) -> tuple[str, str, tuple[tuple[str, Any], ...]]:
        """Deterministic identity for deduplication."""
        items = tuple(sorted(self.payload.items()))
        return (self.kind, self.title, items)

    def transition(self, status: TaskStatus) -> None:
        """Validate lifecycle transitions."""
        allowed: dict[TaskStatus, set[TaskStatus]] = {
            TaskStatus.PENDING: {TaskStatus.QUEUED, TaskStatus.CANCELLED},
            TaskStatus.QUEUED: {
                TaskStatus.WAITING_APPROVAL,
                TaskStatus.SCHEDULED,
                TaskStatus.CANCELLED,
            },
            TaskStatus.WAITING_APPROVAL: {
                TaskStatus.QUEUED,
                TaskStatus.REJECTED,
                TaskStatus.CANCELLED,
            },
            TaskStatus.SCHEDULED: {
                TaskStatus.RUNNING,
                TaskStatus.PAUSED,
                TaskStatus.CANCELLED,
            },
            TaskStatus.RUNNING: {
                TaskStatus.PAUSED,
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
            },
            TaskStatus.PAUSED: {
                TaskStatus.SCHEDULED,
                TaskStatus.CANCELLED,
                TaskStatus.ROLLED_BACK,
            },
            TaskStatus.FAILED: {TaskStatus.ROLLED_BACK},
        }
        if self.status == status:
            return
        if status not in allowed.get(self.status, set()):
            raise ValueError(
                f"invalid transition {self.status.value} -> {status.value}"
            )
        self.status = status
