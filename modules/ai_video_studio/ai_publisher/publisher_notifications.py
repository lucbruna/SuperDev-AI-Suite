"""Publisher Notifications — in-memory notification/alert stream (Volume 7)."""
from __future__ import annotations

import logging
import time
import uuid

logger = logging.getLogger(__name__)

_LEVELS = ("info", "success", "warning", "error")


class PublisherNotifications:
    """Collect publish-related notifications for UI or API consumption."""

    def __init__(self) -> None:
        self._items: list[dict] = []
        self._max_items = 200

    def notify(self, *, message: str, level: str = "info", source: str = "publisher") -> dict:
        """Add a notification to the stream."""
        if level not in _LEVELS:
            level = "info"
        item = {
            "id": uuid.uuid4().hex[:12],
            "ts": time.time(),
            "message": message,
            "level": level,
            "source": source,
        }
        self._items.append(item)
        if len(self._items) > self._max_items:
            self._items = self._items[-self._max_items:]
        return item

    def list(self, *, level: str | None = None, limit: int = 50) -> list[dict]:
        items = self._items
        if level:
            items = [i for i in items if i["level"] == level]
        return list(reversed(items[-limit:]))

    def unread_count(self) -> int:
        return len([i for i in self._items if not i.get("read", False)])

    def mark_read(self, item_id: str) -> bool:
        for item in self._items:
            if item["id"] == item_id:
                item["read"] = True
                return True
        return False

    def stats(self) -> dict[str, int]:
        return {"total": len(self._items), "unread": self.unread_count()}


_NOTIFICATIONS: PublisherNotifications | None = None


def get_publisher_notifications() -> PublisherNotifications:
    """Get the module-level singleton notification stream."""
    global _NOTIFICATIONS
    if _NOTIFICATIONS is None:
        _NOTIFICATIONS = PublisherNotifications()
    return _NOTIFICATIONS
