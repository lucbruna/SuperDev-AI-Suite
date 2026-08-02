from __future__ import annotations

import json
from typing import Any, Callable

from ..api_logger import APILogger
from ..api_registry import APIRegistry
from .connection import WebSocketConnection


class EventEmitter:
    """Simple synchronous event emitter with on/off/once/emit."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, handler: Callable) -> None:
        self._listeners.setdefault(event, []).append(handler)

    def off(self, event: str, handler: Callable) -> None:
        listeners = self._listeners.get(event, [])
        if handler in listeners:
            listeners.remove(handler)

    def once(self, event: str, handler: Callable) -> None:
        def wrapper(data: Any) -> None:
            self.off(event, wrapper)
            handler(data)

        self.on(event, wrapper)

    def emit(self, event: str, data: Any = None) -> list[Any]:
        results: list[Any] = []
        for handler in list(self._listeners.get(event, [])):
            result = handler(data)
            if result is not None:
                results.append(result)
        return results

    def listeners(self, event: str) -> list[Callable]:
        return list(self._listeners.get(event, []))


async def handle_message(
    connection: WebSocketConnection,
    message: str | bytes,
    registry: APIRegistry,
    logger: APILogger,
) -> dict[str, Any] | None:
    """Handle an incoming WebSocket message."""
    try:
        data: dict[str, Any] = json.loads(message if isinstance(message, str) else message.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("Invalid WebSocket message", connection_id=connection.connection_id)
        return {"type": "error", "payload": {"message": "Invalid message format"}}

    msg_type = data.get("type", "")
    payload = data.get("payload", {})
    handler = registry.get_handler(f"ws:{msg_type}") if msg_type else None

    if handler is None:
        return {"type": "error", "payload": {"message": f"Unknown message type: {msg_type}"}}

    try:
        if hasattr(handler, "__call__"):
            result = handler(connection, payload)
            if hasattr(result, "__await__"):
                result = await result
            return {"type": "response", "payload": result} if result is not None else None
    except Exception as e:
        logger.error("WebSocket handler error", msg_type=msg_type, error=str(e))
        return {"type": "error", "payload": {"message": f"Handler error: {str(e)}"}}

    return None
