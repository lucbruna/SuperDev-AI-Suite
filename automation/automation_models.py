"""Data models for the automation engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    EVENT = "event"
    TIME = "time"
    API = "api"
    DATABASE = "database"
    USER = "user"
    CONDITION = "condition"


@dataclass
class WorkflowStep:
    """A single step inside a workflow."""

    step_id: str
    action: str  # e.g. "email.send", "api.call", "agent.run"
    params: dict[str, Any] = field(default_factory=dict)
    next_on_success: str | None = None
    next_on_failure: str | None = None
    timeout: float | None = None


@dataclass
class WorkflowDefinition:
    """A defined workflow with ordered steps."""

    workflow_id: str
    name: str
    description: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)  # trigger ids
    active: bool = True
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "steps": [s.__dict__ for s in self.steps],
            "triggers": list(self.triggers),
            "active": self.active,
            "version": self.version,
            "tags": list(self.tags),
        }


@dataclass
class ExecutionRecord:
    """A single workflow execution."""

    execution_id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: float | None = None
    finished_at: float | None = None
    steps_completed: int = 0
    error: str | None = None
    result: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "steps_completed": self.steps_completed,
            "error": self.error,
            "result": self.result,
        }


@dataclass
class TriggerSpec:
    """Configuration for a workflow trigger."""

    trigger_id: str
    trigger_type: TriggerType
    config: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class TaskRecord:
    """A unit of work dispatched to an executor or agent."""

    task_id: str
    workflow_id: str
    step_id: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class AutomationResult:
    """Result envelope returned by the engine."""

    success: bool
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"success": self.success, "result": self.result, "error": self.error}


@dataclass
class ScheduleSpec:
    """Scheduled execution specification."""

    schedule_id: str
    workflow_id: str
    cron: str = "0 8 * * *"
    interval_seconds: float | None = None
    enabled: bool = True


@dataclass
class AutomationDefinition:
    """A packaged automation (workflow + triggers + schedule)."""

    automation_id: str
    name: str
    category: str = "general"  # business | developer | finance | support | marketing
    workflow: WorkflowDefinition | None = None
    schedule: ScheduleSpec | None = None
    enabled: bool = True
