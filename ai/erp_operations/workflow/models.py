"""Workflow models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StepType(Enum):
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    TASK = "task"
    CONDITION = "condition"
    AUTOMATION = "automation"


class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str = ""
    description: str = ""
    status: WorkflowStatus = WorkflowStatus.DRAFT
    steps: List[Dict[str, Any]] = field(default_factory=list)
    created_by: str = ""
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowStep:
    step_id: str
    workflow_id: str = ""
    name: str = ""
    step_type: StepType = StepType.TASK
    assignee: str = ""
    status: StepStatus = StepStatus.PENDING
    order: int = 0
    required: bool = True
    result: str = ""
    notes: str = ""


@dataclass
class WorkflowInstance:
    instance_id: str
    workflow_id: str = ""
    initiated_by: str = ""
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    current_step: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class ApprovalRecord:
    record_id: str
    step_id: str = ""
    instance_id: str = ""
    approver: str = ""
    decision: str = ""
    comments: str = ""
    decided_at: datetime = field(default_factory=datetime.now)
