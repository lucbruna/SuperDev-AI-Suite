"""Domain models for the Autonomous Developer.

Tasks, plans, file changes and review verdicts are the units of work the
runtime produces, executes and persists. Models are plain dataclasses so the
module keeps zero hard dependencies.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from modules.autonomous_developer.config.constants import (
    OP_CREATE,
    RISK_LOW,
    TASK_BLOCKED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_IN_PROGRESS,
    TASK_PENDING,
)


@dataclass(slots=True)
class FileChange:
    """One file write planned or produced by the developer."""

    path: str
    content: str | None = None
    operation: str = OP_CREATE
    old_content: str | None = None
    reason: str = ""

    @property
    def content_size(self) -> int:
        return len(self.content) if self.content else 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "operation": self.operation,
            "reason": self.reason,
            "content_size": self.content_size,
        }


@dataclass(slots=True)
class Task:
    """A single unit of autonomous work."""

    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    description: str = ""
    priority: str = "medium"  # low | medium | high | critical
    status: str = TASK_PENDING
    risk: str = RISK_LOW  # low | medium | high | critical
    phase: str = ""
    depends_on: list[str] = field(default_factory=list)
    files: list[FileChange] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    error: str = ""

    @property
    def elapsed_seconds(self) -> float:
        if self.started_at is None:
            return 0.0
        end = self.finished_at or time.time()
        return round(end - self.started_at, 3)

    @property
    def is_done(self) -> bool:
        return self.status in {TASK_COMPLETED, TASK_FAILED}

    def start(self) -> None:
        self.status = TASK_IN_PROGRESS
        self.started_at = time.time()

    def complete(self) -> None:
        self.status = TASK_COMPLETED
        self.finished_at = time.time()

    def fail(self, message: str = "") -> None:
        self.status = TASK_FAILED
        self.error = message
        self.finished_at = time.time()

    def block(self, message: str = "") -> None:
        self.status = TASK_BLOCKED
        self.error = message

    def add_file(self, change: FileChange) -> None:
        self.files.append(change)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "risk": self.risk,
            "phase": self.phase,
            "depends_on": list(self.depends_on),
            "files": [f.to_dict() for f in self.files],
            "elapsed_seconds": self.elapsed_seconds,
            "error": self.error,
        }


@dataclass(slots=True)
class TaskPlan:
    """A goal decomposed into ordered tasks."""

    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal: str = ""
    tasks: list[Task] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def by_status(self, status: str) -> list[Task]:
        return [task for task in self.tasks if task.status == status]

    def summary(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for task in self.tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "task_count": len(self.tasks),
            "by_status": counts,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "created_at": self.created_at,
            "tasks": [task.to_dict() for task in self.tasks],
        }


@dataclass(slots=True)
class ReviewVerdict:
    """Outcome of reviewing a task's changes."""

    review_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    task_id: str = ""
    verdict: str = "changes_requested"  # approved | changes_requested | rejected
    comments: str = ""
    issues: list[str] = field(default_factory=list)
    reviewer: str = "autonomous_developer"
    timestamp: float = field(default_factory=time.time)

    @property
    def approved(self) -> bool:
        return self.verdict == "approved"

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "task_id": self.task_id,
            "verdict": self.verdict,
            "comments": self.comments,
            "issues": list(self.issues),
            "reviewer": self.reviewer,
            "timestamp": self.timestamp,
        }
