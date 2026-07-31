"""Notification Engine - Core notification system."""

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NotificationType(Enum):
    PUSH = "push"
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class Notification:
    notification_id: str
    title: str
    message: str
    type: NotificationType = NotificationType.PUSH
    priority: NotificationPriority = NotificationPriority.NORMAL
    target_device: str = ""
    target_user: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    read: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: datetime | None = None


class NotificationEngine:
    def __init__(self):
        self.notifications: list[Notification] = []
        self.handlers: dict[NotificationType, Callable] = {}
        self.rules: list[dict[str, Any]] = []

    def send(
        self,
        title: str,
        message: str,
        type: NotificationType = NotificationType.PUSH,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        **kwargs,
    ) -> Notification:
        notif_id = hashlib.sha256(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        notif = Notification(
            notification_id=notif_id, title=title, message=message, type=type, priority=priority, **kwargs
        )
        self.notifications.append(notif)
        handler = self.handlers.get(type)
        if handler:
            try:
                handler(notif)
                notif.sent_at = datetime.now()
            except Exception:
                pass
        return notif

    def register_handler(self, type: NotificationType, handler: Callable) -> None:
        self.handlers[type] = handler

    def add_rule(self, rule: dict[str, Any]) -> None:
        self.rules.append(rule)

    def mark_read(self, notification_id: str) -> bool:
        for notif in self.notifications:
            if notif.notification_id == notification_id:
                notif.read = True
                return True
        return False

    def get_unread(self, user: str = None) -> list[Notification]:
        unread = [n for n in self.notifications if not n.read]
        if user:
            unread = [n for n in unread if n.target_user == user]
        return unread

    def get_notifications(
        self, type: NotificationType = None, user: str = None, limit: int = 100
    ) -> list[Notification]:
        notifs = self.notifications
        if type:
            notifs = [n for n in notifs if n.type == type]
        if user:
            notifs = [n for n in notifs if n.target_user == user]
        return notifs[-limit:]

    def count(self) -> int:
        return len(self.notifications)

    def count_unread(self) -> int:
        return len([n for n in self.notifications if not n.read])
