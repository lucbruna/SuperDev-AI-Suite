from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from backend.utils.uuid_utils import generate_uuid


class NotificationType(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Notification:
    id: str
    user_id: str
    title: str
    message: str
    notification_type: NotificationType
    is_read: bool = False
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class NotificationManager:
    """In-memory notification manager."""

    def __init__(self):
        self._notifications: dict[str, Notification] = {}

    def create(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        data: dict[str, Any] | None = None,
    ) -> Notification:
        notif = Notification(
            id=generate_uuid(),
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            data=data or {},
        )
        self._notifications[notif.id] = notif
        return notif

    def get(self, notification_id: str) -> Notification | None:
        return self._notifications.get(notification_id)

    def list_for_user(self, user_id: str, unread_only: bool = False) -> list[Notification]:
        notifs = [n for n in self._notifications.values() if n.user_id == user_id]
        if unread_only:
            notifs = [n for n in notifs if not n.is_read]
        return sorted(notifs, key=lambda n: n.created_at, reverse=True)

    def mark_read(self, notification_id: str) -> bool:
        notif = self._notifications.get(notification_id)
        if notif:
            notif.is_read = True
            return True
        return False

    def mark_all_read(self, user_id: str) -> int:
        count = 0
        for notif in self._notifications.values():
            if notif.user_id == user_id and not notif.is_read:
                notif.is_read = True
                count += 1
        return count

    def delete(self, notification_id: str) -> bool:
        if notification_id in self._notifications:
            del self._notifications[notification_id]
            return True
        return False

    def unread_count(self, user_id: str) -> int:
        return sum(1 for n in self._notifications.values() if n.user_id == user_id and not n.is_read)


notification_manager = NotificationManager()
