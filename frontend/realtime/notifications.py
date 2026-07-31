from __future__ import annotations

import logging
from typing import Any, Callable

from .event_stream import EventStream


class RealtimeNotifications:
    """Real-time notification delivery over the event stream."""

    def __init__(self, events: EventStream) -> None:
        self._log = logging.getLogger("superdev.frontend.realtime.notifications")
        self._events = events
        self._channel = "notifications"
        self._delivered: list[dict[str, Any]] = []

    def push(self, kind: str, message: str, **data: Any) -> None:
        notification = {"kind": kind, "message": message, **data}
        self._delivered.append(notification)
        self._events.publish(self._channel, notification)

    def subscribe(self, handler: Callable[[str, Any], None]) -> None:
        self._events.subscribe(self._channel, handler)

    def list(self, limit: int | None = None) -> list[dict[str, Any]]:
        notifications = list(self._delivered)
        if limit is not None:
            notifications = notifications[-limit:]
        return notifications

    def clear(self) -> None:
        self._delivered.clear()
