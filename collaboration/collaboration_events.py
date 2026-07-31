"""Event bus for Collaboration & Team Workspace lifecycle events."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable


class CollaborationEventType(Enum):
    WORKSPACE_CREATED = "workspace.created"
    WORKSPACE_UPDATED = "workspace.updated"
    TEAM_CREATED = "team.created"
    MEMBER_JOINED = "member.joined"
    MEMBER_LEFT = "member.left"
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    COMMENT_ADDED = "comment.added"
    REVIEW_CREATED = "review.created"
    REVIEW_DECIDED = "review.decided"
    APPROVAL_STARTED = "approval.started"
    APPROVAL_DECIDED = "approval.decided"
    MESSAGE_SENT = "message.sent"
    DOCUMENT_CREATED = "document.created"
    DOCUMENT_UPDATED = "document.updated"
    AGENT_ACTION = "agent.action"


class CollaborationEvents:
    """Lightweight in-process pub/sub."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.collaboration.events")
        self._listeners: dict[CollaborationEventType,
                              list[Callable[[dict[str, Any]], None]]] = {}

    def on(self, event_type: CollaborationEventType,
           listener: Callable[[dict[str, Any]], None]) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def off(self, event_type: CollaborationEventType,
            listener: Callable[[dict[str, Any]], None]) -> None:
        listeners = self._listeners.get(event_type, [])
        if listener in listeners:
            listeners.remove(listener)

    def publish(self, event_type: CollaborationEventType,
                data: dict[str, Any] | None = None) -> None:
        payload = {"type": event_type.value, **(data or {})}
        for listener in list(self._listeners.get(event_type, [])):
            try:
                listener(payload)
            except Exception as exc:  # noqa: BLE001
                self._log.warning("listener failed for %s: %s",
                                  event_type.value, exc)

    def once(self, event_type: CollaborationEventType,
             listener: Callable[[dict[str, Any]], None]) -> None:
        def wrapper(data: dict[str, Any]) -> None:
            self.off(event_type, wrapper)
            listener(data)

        self.on(event_type, wrapper)

    def listener_count(self, event_type: CollaborationEventType) -> int:
        return len(self._listeners.get(event_type, []))
