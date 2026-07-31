"""Notifications for members and agents."""

from __future__ import annotations

import time
from typing import Any

from collaboration.collaboration_protocols import new_id


class Notification:
    """A single notification targeting a member or agent."""

    def __init__(self, recipient_id: str, kind: str,
                 title: str, body: str = "",
                 reference_id: str = "") -> None:
        self.notification_id = new_id("notif")
        self.recipient_id = recipient_id
        self.kind = kind
        self.title = title
        self.body = body
        self.reference_id = reference_id
        self.created_at = time.time()
        self.read = False

    def mark_read(self) -> None:
        self.read = True

    def to_dict(self) -> dict[str, Any]:
        return {"notification_id": self.notification_id,
                "recipient_id": self.recipient_id, "kind": self.kind,
                "title": self.title, "body": self.body,
                "reference_id": self.reference_id, "read": self.read,
                "created_at": self.created_at}


class NotificationManager:
    """Stores notifications and tracks read state."""

    def __init__(self, max_per_recipient: int = 200) -> None:
        self.max_per_recipient = max_per_recipient
        self._notifications: dict[str, list[Notification]] = {}

    def notify(self, recipient_id: str, kind: str, title: str,
               body: str = "", reference_id: str = "") -> Notification:
        notification = Notification(recipient_id, kind, title, body,
                                    reference_id)
        bucket = self._notifications.setdefault(recipient_id, [])
        bucket.append(notification)
        if len(bucket) > self.max_per_recipient:
            self._notifications[recipient_id] = bucket[
                -self.max_per_recipient:]
        return notification

    def for_recipient(self, recipient_id: str) -> list[Notification]:
        return list(self._notifications.get(recipient_id, []))

    def unread(self, recipient_id: str) -> list[Notification]:
        return [n for n in self.for_recipient(recipient_id) if not n.read]

    def mark_read(self, notification_id: str) -> None:
        for bucket in self._notifications.values():
            for notification in bucket:
                if notification.notification_id == notification_id:
                    notification.mark_read()
                    return

    def mark_all_read(self, recipient_id: str) -> None:
        for notification in self.for_recipient(recipient_id):
            notification.mark_read()

    def count(self) -> int:
        return sum(len(v) for v in self._notifications.values())
