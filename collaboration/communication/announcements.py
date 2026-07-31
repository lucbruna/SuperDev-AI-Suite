"""Announcements broadcast to channels or workspaces."""

from __future__ import annotations

import time
from typing import Any

from collaboration.collaboration_models import MessageKind, MessageRecord
from collaboration.collaboration_protocols import new_id


class Announcement:
    """A broadcast message with a title."""

    def __init__(self, workspace_id: str, title: str, body: str,
                 author_id: str, target: str = "workspace") -> None:
        self.announcement_id = new_id("ann")
        self.workspace_id = workspace_id
        self.title = title
        self.body = body
        self.author_id = author_id
        self.target = target
        self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {"announcement_id": self.announcement_id,
                "workspace_id": self.workspace_id, "title": self.title,
                "body": self.body, "author_id": self.author_id,
                "target": self.target, "created_at": self.created_at}


class AnnouncementManager:
    """Creates and lists announcements (and mirrors them as messages)."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry
        self._announcements: list[Announcement] = []

    def announce(self, workspace_id: str, title: str, body: str,
                 author_id: str, channel_id: str = "",
                 target: str = "workspace") -> Announcement:
        announcement = Announcement(workspace_id, title, body, author_id,
                                    target)
        self._announcements.append(announcement)
        if channel_id and self.registry is not None:
            message = MessageRecord(
                message_id=new_id("msg"), channel_id=channel_id,
                author_id=author_id,
                body=f"ANÚNCIO: {title}\n{body}",
                kind=MessageKind.NOTIFICATION)
            self.registry.add_message(message)
        return announcement

    def list(self, workspace_id: str | None = None) -> list[Announcement]:
        if workspace_id is None:
            return list(self._announcements)
        return [a for a in self._announcements
                if a.workspace_id == workspace_id]

    def count(self) -> int:
        return len(self._announcements)
