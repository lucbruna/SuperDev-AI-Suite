"""Deterministic websocket message protocol and simulated hub."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

__all__ = [
    "MessageBuilder",
    "WebSocketHub",
    "WebSocketMessage",
    "decode",
    "encode",
]


@dataclass(slots=True)
class WebSocketMessage:
    """A single typed message with a payload and unique id."""

    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: uuid4().hex)


def encode(message: WebSocketMessage) -> str:
    """Serialize a message to a deterministic JSON string."""
    return json.dumps(
        {
            "type": message.type,
            "payload": message.payload,
            "message_id": message.message_id,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def decode(raw: str) -> WebSocketMessage:
    """Parse a serialized message back into a :class:`WebSocketMessage`."""
    data = json.loads(raw)
    return WebSocketMessage(
        type=str(data["type"]),
        payload=dict(data.get("payload") or {}),
        message_id=str(data.get("message_id", "")),
    )


class MessageBuilder:
    """Builds typed messages for common pipeline events."""

    @staticmethod
    def progress(payload: dict[str, Any]) -> WebSocketMessage:
        return WebSocketMessage(type="progress", payload=payload)

    @staticmethod
    def event(payload: dict[str, Any]) -> WebSocketMessage:
        return WebSocketMessage(type="event", payload=payload)

    @staticmethod
    def result(payload: dict[str, Any]) -> WebSocketMessage:
        return WebSocketMessage(type="result", payload=payload)


class WebSocketHub:
    """In-memory simulated hub: connected clients and message history."""

    def __init__(self) -> None:
        self._clients: set[str] = set()
        self._messages: list[WebSocketMessage] = []

    def connect(self, client_id: str) -> bool:
        """Register a client; idempotent, returns whether it was added."""
        if client_id in self._clients:
            return False
        self._clients.add(client_id)
        return True

    def disconnect(self, client_id: str) -> bool:
        """Remove a client; returns whether it was present."""
        if client_id not in self._clients:
            return False
        self._clients.discard(client_id)
        return True

    def clients(self) -> list[str]:
        return sorted(self._clients)

    def send(self, message: WebSocketMessage) -> WebSocketMessage:
        self._messages.append(message)
        return message

    def broadcast(
        self, type: str, payload: dict[str, Any] | None = None
    ) -> WebSocketMessage:
        message = WebSocketMessage(type=type, payload=dict(payload or {}))
        self._messages.append(message)
        return message

    def poll(self) -> list[WebSocketMessage]:
        """Drain and return every pending message."""
        pending = list(self._messages)
        self._messages.clear()
        return pending

    def count(self) -> int:
        return len(self._messages)
