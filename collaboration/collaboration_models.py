"""Data models for the Collaboration & Team Workspace Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemberKind(Enum):
    HUMAN = "human"
    AGENT = "agent"


class MemberRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    SECURITY = "security"
    ANALYST = "analyst"
    VIEWER = "viewer"


class MemberStatus(Enum):
    INVITED = "invited"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    LEFT = "left"


class TeamKind(Enum):
    DEVELOPMENT = "development"
    QUALITY = "quality"
    SECURITY = "security"
    OPERATIONS = "operations"
    MANAGEMENT = "management"
    AGENTS = "agents"


class ProjectStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    DONE = "done"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ReviewKind(Enum):
    CODE = "code"
    DOCUMENT = "document"
    SECURITY = "security"
    PROCESS = "process"


class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ChannelKind(Enum):
    CHANNEL = "channel"
    DIRECT = "direct"


class MessageKind(Enum):
    CHAT = "chat"
    NOTIFICATION = "notification"
    SYSTEM = "system"


class EntityKind(Enum):
    WORKSPACE = "workspace"
    TEAM = "team"
    PROJECT = "project"
    TASK = "task"
    COMMENT = "comment"
    REVIEW = "review"
    APPROVAL = "approval"
    MESSAGE = "message"
    DOCUMENT = "document"


@dataclass
class WorkspaceRecord:
    workspace_id: str
    name: str
    owner_id: str
    description: str = ""
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0


@dataclass
class TeamRecord:
    team_id: str
    workspace_id: str
    name: str
    kind: TeamKind = TeamKind.DEVELOPMENT
    lead_id: str | None = None
    description: str = ""


@dataclass
class MemberRecord:
    member_id: str
    workspace_id: str
    name: str
    kind: MemberKind = MemberKind.HUMAN
    role: MemberRole = MemberRole.DEVELOPER
    email: str = ""
    status: MemberStatus = MemberStatus.ACTIVE
    skills: list[str] = field(default_factory=list)
    team_ids: list[str] = field(default_factory=list)
    availability: float = 1.0  # 0..1


@dataclass
class ProjectRecord:
    project_id: str
    workspace_id: str
    name: str
    status: ProjectStatus = ProjectStatus.PLANNING
    description: str = ""
    progress: float = 0.0  # 0..100
    start_date: str = ""
    target_date: str = ""
    owner_id: str = ""


@dataclass
class TaskRecord:
    task_id: str
    project_id: str
    workspace_id: str
    title: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: str | None = None
    created_by: str = ""
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    progress: float = 0.0  # 0..100
    parent_id: str | None = None


@dataclass
class CommentRecord:
    comment_id: str
    target_kind: EntityKind
    target_id: str
    author_id: str
    body: str
    mentions: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    reactions: dict[str, list[str]] = field(default_factory=dict)
    created_at: float = 0.0


@dataclass
class ReviewRecord:
    review_id: str
    target_kind: ReviewKind
    target_id: str
    author_id: str
    status: ReviewStatus = ReviewStatus.PENDING
    score: float = 0.0  # 0..100
    findings: list[dict[str, Any]] = field(default_factory=list)
    created_at: float = 0.0


@dataclass
class ApprovalRecord:
    approval_id: str
    target_kind: EntityKind
    target_id: str
    flow: str = "manager"
    status: ApprovalStatus = ApprovalStatus.PENDING
    steps: list[dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    requested_by: str = ""
    decided_by: str | None = None
    decided_at: float = 0.0
    reason: str = ""


@dataclass
class ChannelRecord:
    channel_id: str
    workspace_id: str
    name: str
    kind: ChannelKind = ChannelKind.CHANNEL
    members: list[str] = field(default_factory=list)
    topic: str = ""


@dataclass
class MessageRecord:
    message_id: str
    channel_id: str
    author_id: str
    body: str
    kind: MessageKind = MessageKind.CHAT
    mentions: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    created_at: float = 0.0


@dataclass
class KnowledgeRecord:
    document_id: str
    workspace_id: str
    title: str
    body: str = ""
    author_id: str = ""
    tags: list[str] = field(default_factory=list)
    version: int = 1
    updated_at: float = 0.0
