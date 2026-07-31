from __future__ import annotations

import logging
from typing import Any, Callable

from .event_stream import EventStream
from .live_updates import LiveUpdates
from .notifications import RealtimeNotifications
from .websocket_client import WebSocketClient


class RealtimeEngine:
    """Coordinates all realtime communication channels."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.realtime")
        self.events = EventStream()
        self.notifications = RealtimeNotifications(self.events)
        self.live_updates = LiveUpdates(self.events)
        self.websocket = WebSocketClient()

    def connect(self, url: str) -> bool:
        return self.websocket.connect(url)

    def disconnect(self) -> bool:
        return self.websocket.disconnect()

    def subscribe(self, channel: str, handler: Callable[[str, Any], None]) -> None:
        self.events.subscribe(channel, handler)

    def publish(self, channel: str, data: Any) -> None:
        self.events.publish(channel, data)

    def start_live(self, interval: float = 1.0) -> bool:
        return self.live_updates.start(interval)

    def stop_live(self) -> bool:
        return self.live_updates.stop()

    def status(self) -> dict[str, Any]:
        return {
            "connected": self.websocket.is_connected(),
            "subscribers": len(self.events.subscriber_count()),
            "live_updates": self.live_updates.is_running(),
        }
