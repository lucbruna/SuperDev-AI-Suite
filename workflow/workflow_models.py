from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class WorkflowTriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULE = "schedule"
    EVENT = "event"
    WEBHOOK = "webhook"
    FILE = "file"
    DATABASE = "database"
    AI = "ai"


@dataclass
class WorkflowStep:
    id: str
    name: str
    action: str
    depends_on: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 300.0
    result: dict[str, Any] | None = None
    error: str | None = None


@dataclass
class WorkflowTrigger:
    type: WorkflowTriggerType
    config: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class WorkflowState:
    current_step: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    failed_steps: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    triggers: list[WorkflowTrigger] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0
