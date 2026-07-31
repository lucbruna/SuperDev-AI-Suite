from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Notification:
    """A single notification message."""

    message: str
    kind: str = "info"  # info | success | warning | error
    title: str = ""
    created_at: float = field(default_factory=time.time)
    duration_ms: int = 5000
    actions: list[dict[str, Any]] = field(default_factory=list)


class Notifications:
    """Manages notification queue and rendering specs."""

    def __init__(self) -> None:
        self._queue: list[Notification] = []
        self._listeners: list[Callable[[Notification], None]] = []

    def notify(self, message: str, kind: str = "info", **kwargs: Any) -> Notification:
        notification = Notification(message=message, kind=kind, **kwargs)
        self._queue.append(notification)
        for listener in self._listeners:
            listener(notification)
        return notification

    def success(self, message: str, **kwargs: Any) -> Notification:
        return self.notify(message, "success", **kwargs)

    def warning(self, message: str, **kwargs: Any) -> Notification:
        return self.notify(message, "warning", **kwargs)

    def error(self, message: str, **kwargs: Any) -> Notification:
        return self.notify(message, "error", **kwargs)

    def on_notify(self, listener: Callable[[Notification], None]) -> None:
        self._listeners.append(listener)

    def list(self, limit: int | None = None) -> list[Notification]:
        notifications = list(self._queue)
        if limit is not None:
            notifications = notifications[-limit:]
        return notifications

    def dismiss(self, notification: Notification) -> bool:
        if notification in self._queue:
            self._queue.remove(notification)
            return True
        return False

    def clear(self) -> None:
        self._queue.clear()

    def build(self, notification: Notification) -> dict[str, Any]:
        return {"type": "notification", **vars(notification)}
