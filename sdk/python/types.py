"""Type definitions for the SuperDev Python SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, Iterator, TypeVar

T = TypeVar("T")


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


class WorkflowRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class User:
    id: str
    email: str
    name: str
    avatar_url: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Organization:
    id: str
    name: str
    slug: str
    plan: str = "free"
    created_at: datetime | None = None


@dataclass
class Project:
    id: str
    name: str
    description: str = ""
    organization_id: str = ""
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Agent:
    id: str
    name: str
    type: str = "general"
    status: AgentStatus = AgentStatus.IDLE
    config: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None


@dataclass
class Provider:
    id: str
    name: str
    type: str
    is_enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)
    health: str = "healthy"


@dataclass
class ProviderHealth:
    provider_id: str
    status: str
    latency_ms: float = 0.0
    last_checked: datetime | None = None
    error: str | None = None


@dataclass
class Plugin:
    id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    is_installed: bool = False
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    id: str
    name: str
    description: str = ""
    graph: dict[str, Any] = field(default_factory=dict)
    status: str = "draft"
    version: int = 1
    created_at: datetime | None = None


@dataclass
class WorkflowRun:
    id: str
    workflow_id: str
    status: WorkflowRunStatus = WorkflowRunStatus.PENDING
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None


@dataclass
class ChatMessage:
    role: MessageRole
    content: str
    timestamp: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatResponse:
    message: str
    model: str = ""
    provider: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = ""


@dataclass
class StreamingChunk:
    delta: str = ""
    model: str = ""
    finish_reason: str | None = None
    usage: dict[str, int] = field(default_factory=dict)


@dataclass
class Conversation:
    id: str
    title: str = ""
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: datetime | None = None


@dataclass
class EmbeddingRequest:
    input: str | list[str]
    model: str = "text-embedding-3-small"


@dataclass
class EmbeddingResponse:
    embeddings: list[list[float]]
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)


@dataclass
class RunWorkflowRequest:
    workflow_id: str
    inputs: dict[str, Any] = field(default_factory=dict)
    timeout: int = 3600


@dataclass
class Deployment:
    id: str
    project_id: str
    status: str = "pending"
    environment: str = "production"
    url: str | None = None
    created_at: datetime | None = None


@dataclass
class PaginatedResponse(Generic[T]):
    items: list[T]
    total: int = 0
    page: int = 1
    page_size: int = 20
    has_next: bool = False
    has_previous: bool = False


@dataclass
class ErrorResponse:
    error: str
    message: str = ""
    status_code: int = 0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditLog:
    id: str
    action: str
    user_id: str
    resource_type: str = ""
    resource_id: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime | None = None


@dataclass
class Notification:
    id: str
    type: str
    title: str
    message: str = ""
    read: bool = False
    created_at: datetime | None = None
