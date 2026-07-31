"""Models for the Agent Orchestration Engine (Volume 31)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    BLOCKED = "blocked"
    ERROR = "error"
    OFFLINE = "offline"


class TaskStatus(Enum):
    PENDING = "pending"
    PLANNED = "planned"
    QUEUED = "queued"
    RUNNING = "running"
    APPROVAL_REQUIRED = "approval_required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(Enum):
    DIRECT = "direct"
    BROADCAST = "broadcast"
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        return {"low": 0, "medium": 1, "high": 2, "critical": 3}[self.value]


@dataclass
class AgentCapability:
    """A skill an agent can execute."""
    name: str
    description: str = ""
    tools: list[str] = field(default_factory=list)
    max_load: int = 1


@dataclass
class AgentProfile:
    """Definition of an autonomous agent."""
    agent_id: str
    name: str
    objective: str = ""
    role: str = "worker"
    capabilities: list[AgentCapability] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    knowledge: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_capability(self, name: str) -> bool:
        return any(capability.name == name for capability in self.capabilities)

    def can(self, permission: str) -> bool:
        return permission in self.permissions or "*" in self.permissions


@dataclass
class AgentTask:
    """A unit of work assigned to an agent."""
    task_id: str
    title: str
    description: str = ""
    agent_id: str = ""
    plan_id: str = ""
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    risk_level: RiskLevel = RiskLevel.LOW
    approval_required: bool = False
    dependencies: list[str] = field(default_factory=list)
    attempts: int = 0
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    result: Any = None
    error: str = ""


@dataclass
class AgentMessage:
    """A message exchanged between agents."""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType = MessageType.DIRECT
    content: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0


@dataclass
class ExecutionResult:
    """Outcome of an agent task execution."""
    result_id: str
    task_id: str
    agent_id: str
    status: TaskStatus = TaskStatus.COMPLETED
    output: Any = None
    error: str = ""
    duration: float = 0.0


@dataclass
class EvaluationReport:
    """Scorecard for an agent after an evaluation round."""
    evaluation_id: str
    agent_id: str
    accuracy: float = 0.0
    errors: int = 0
    avg_time: float = 0.0
    quality_score: float = 0.0
    feedback: str = ""
    created_at: float = 0.0


@dataclass
class Lesson:
    """A learned improvement recorded by the learning subsystem."""
    lesson_id: str
    agent_id: str
    topic: str = ""
    error: str = ""
    solution: str = ""
    applied: bool = False
    created_at: float = 0.0
