"""Data models for task orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class OrchestrationTask:
    """A unit of work assigned to an agent."""

    task_id: str
    name: str
    agent_id: str
    kind: str  # plan | implement | test | security_review | deploy
    depends_on: list[str] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "agent_id": self.agent_id,
            "kind": self.kind,
            "depends_on": list(self.depends_on),
            "status": self.status.value,
            "error": self.error,
        }


@dataclass
class OrchestrationPlan:
    """A set of tasks executed to accomplish a goal."""

    plan_id: str
    goal: str
    tasks: list[OrchestrationTask] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING

    def task(self, task_id: str) -> OrchestrationTask | None:
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def by_agent(self, agent_id: str) -> list[OrchestrationTask]:
        return [t for t in self.tasks if t.agent_id == agent_id]
