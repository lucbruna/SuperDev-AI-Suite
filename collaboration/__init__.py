"""Collaboration & Team Workspace Engine (Volume 26).

Public API for collaborative work where humans and AI agents work
together: workspaces, teams, members, projects, tasks, comments,
reviews, approvals, communication and knowledge.
"""
from __future__ import annotations

from .collaboration_config import CollaborationConfig
from .collaboration_context import CollaborationContext
from .collaboration_engine import CollaborationEngine
from .collaboration_events import CollaborationEventType, CollaborationEvents
from .collaboration_factory import build_engine
from .collaboration_interfaces import (AgentCollaborator, ApprovalFlow,
                                       CommentHandler, KnowledgeSink,
                                       MessageSink, ProjectProvider,
                                       Reviewer, TaskProvider, TeamProvider,
                                       WorkspaceProvider)
from .collaboration_logger import get_logger
from .collaboration_manager import CollaborationManager
from .collaboration_metrics import CollaborationMetrics
from .collaboration_models import (ApprovalRecord, ApprovalStatus,
                                   ChannelKind, ChannelRecord, CommentRecord,
                                   EntityKind, KnowledgeRecord, MemberKind,
                                   MemberRecord, MemberRole, MemberStatus,
                                   MessageKind, MessageRecord, ProjectRecord,
                                   ProjectStatus, ReviewKind, ReviewRecord,
                                   ReviewStatus, TaskPriority, TaskRecord,
                                   TaskStatus, TeamKind, TeamRecord,
                                   WorkspaceRecord)
from .collaboration_protocols import (coerce_bool, coerce_number,
                                      extract_mentions, new_id, safe_get)
from .collaboration_registry import CollaborationRegistry
from .collaboration_runtime import CollaborationRuntime
from .collaboration_security import CollaborationSecurity

__all__ = [
    "AgentCollaborator",
    "ApprovalFlow",
    "ApprovalRecord",
    "ApprovalStatus",
    "ChannelKind",
    "ChannelRecord",
    "CollaborationConfig",
    "CollaborationContext",
    "CollaborationEngine",
    "CollaborationEventType",
    "CollaborationEvents",
    "CollaborationManager",
    "CollaborationMetrics",
    "CollaborationRegistry",
    "CollaborationRuntime",
    "CollaborationSecurity",
    "CommentHandler",
    "CommentRecord",
    "EntityKind",
    "KnowledgeRecord",
    "KnowledgeSink",
    "MemberKind",
    "MemberRecord",
    "MemberRole",
    "MemberStatus",
    "MessageKind",
    "MessageRecord",
    "MessageSink",
    "ProjectProvider",
    "ProjectRecord",
    "ProjectStatus",
    "ReviewKind",
    "ReviewRecord",
    "ReviewStatus",
    "Reviewer",
    "TaskPriority",
    "TaskProvider",
    "TaskRecord",
    "TaskStatus",
    "TeamKind",
    "TeamProvider",
    "TeamRecord",
    "WorkspaceProvider",
    "WorkspaceRecord",
    "build_engine",
    "coerce_bool",
    "coerce_number",
    "extract_mentions",
    "get_logger",
    "new_id",
    "safe_get",
]
