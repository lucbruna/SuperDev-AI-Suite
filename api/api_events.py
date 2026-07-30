from __future__ import annotations

import time
from enum import Enum
from typing import Any, Callable


class APIEventType(Enum):
    REQUEST_STARTED = "request.started"
    REQUEST_COMPLETED = "request.completed"
    REQUEST_FAILED = "request.failed"
    CONNECTION_OPENED = "connection.opened"
    CONNECTION_CLOSED = "connection.closed"
    AUTH_SUCCESS = "auth.success"
    AUTH_FAILURE = "auth.failure"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"
    SERVER_STARTED = "server.started"
    SERVER_STOPPED = "server.stopped"
    ROUTE_REGISTERED = "route.registered"
    ERROR_OCCURRED = "error.occurred"
    WEBHOOK_SENT = "webhook.sent"
    WEBSOCKET_MESSAGE = "websocket.message"


class APIEventBus:
    """Event bus for API layer events with pub/sub."""

    def __init__(self) -> None:
        self._handlers: dict[APIEventType, list[Callable]] = {}

    def on(self, event_type: APIEventType, handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def off(self, event_type: APIEventType, handler: Callable) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    async def emit(self, event_type: APIEventType, data: dict[str, Any] | None = None) -> None:
        handlers = self._handlers.get(event_type, [])
        payload = {"event": event_type.value, "timestamp": time.time(), "data": data or {}}
        for handler in handlers:
            try:
                result = handler(payload)
                if hasattr(result, "__await__"):
                    await result
            except Exception:
                pass

    def list_handlers(self) -> dict[str, int]:
        return {e.value: len(h) for e, h in self._handlers.items()}

    def to_dict(self) -> dict[str, Any]:
        return {"registered_events": [e.value for e in self._handlers], "handler_count": sum(len(h) for h in self._handlers.values())}
