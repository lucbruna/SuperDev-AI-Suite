"""
WebSocket Service
"""

from collections.abc import Callable
from enum import Enum
from typing import Any


class WSStatus(Enum):
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class WebSocketService:
    def __init__(self):
        self.status = WSStatus.DISCONNECTED
        self.url: str = ""
        self.listeners: dict[str, list[Callable]] = {}

    def connect(self, url: str) -> None:
        self.url = url
        self.status = WSStatus.CONNECTED
        self._emit("connected", {})

    def disconnect(self) -> None:
        self.status = WSStatus.DISCONNECTED
        self._emit("disconnected", {})

    def send(self, event: str, data: Any) -> None:
        self._emit("message", {"event": event, "data": data})

    def on(self, event: str, callback: Callable) -> None:
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    def _emit(self, event: str, data: dict[str, Any]) -> None:
        for cb in self.listeners.get(event, []):
            cb(data)

    def render(self) -> dict[str, Any]:
        return {"status": self.status.value, "url": self.url}
