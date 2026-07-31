"""
WebSocket Manager
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class WebSocketState(Enum):
    CONNECTING = "connecting"
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"


@dataclass
class WSMessage:
    event: str
    data: Any
    id: str = ""


class WebSocketManager:
    def __init__(self):
        self.state = WebSocketState.CLOSED
        self.url: str = ""
        self.listeners: dict[str, list[Callable]] = {}
        self.message_queue: list[WSMessage] = []
        self.reconnect_attempts = 0
        self.max_reconnect = 5

    def connect(self, url: str) -> None:
        self.url = url
        self.state = WebSocketState.CONNECTING
        self.state = WebSocketState.OPEN
        self._emit("open", {})

    def disconnect(self) -> None:
        self.state = WebSocketState.CLOSED
        self._emit("close", {})

    def send(self, event: str, data: Any) -> None:
        msg = WSMessage(event=event, data=data)
        self.message_queue.append(msg)
        self._emit("message", msg)

    def on(self, event: str, callback: Callable) -> None:
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    def _emit(self, event: str, data: Any) -> None:
        for cb in self.listeners.get(event, []):
            cb(data)

    def render(self) -> dict[str, Any]:
        return {"state": self.state.value, "url": self.url, "queueLength": len(self.message_queue)}
