"""TaskRequest — the submission contract used by callers of the orchestrator."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from modules.super_ai_orchestrator.core.task import Task


@dataclass(slots=True)
class TaskRequest:
    """How external callers (API, CLI, other modules) submit work.

    Attributes:
        kind: task kind (``develop``, ``repair``, ``evolve``, ...).
        title: human-readable title.
        payload: arbitrary structured input.
        priority: urgency 1..10 (defaults to orchestrator default).
        owner_hint: optional preferred owner; the Decision Engine may still
            choose another agent if capability routing disagrees.
        require_approval: whether this task must pass the governance gate
            (defaults to the orchestrator-wide setting).
    """

    kind: str
    title: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int | None = None
    owner_hint: str | None = None
    require_approval: bool | None = None

    def to_task(self, default_priority: int = 5) -> Task:
        return Task(
            kind=self.kind,
            title=self.title,
            payload=self.payload,
            priority=self.priority if self.priority is not None else default_priority,
        )
