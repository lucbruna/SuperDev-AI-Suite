"""AIOS Message Router — typed request/reply dispatch.

Routes typed messages to registered handlers (one handler per message
type). Used for direct service-to-service and agent-to-service calls.
"""

from __future__ import annotations

import inspect
import uuid
from typing import Any, Awaitable, Callable

MessageHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]


class MessageRouter:
    """Direct message dispatch by message type."""

    def __init__(self) -> None:
        self._handlers: dict[str, MessageHandler] = {}
        self._history: list[dict[str, Any]] = []

    def register(self, message_type: str, handler: MessageHandler) -> "MessageRouter":
        self._handlers[message_type] = handler
        return self

    def unregister(self, message_type: str) -> None:
        self._handlers.pop(message_type, None)

    def types(self) -> list[str]:
        return sorted(self._handlers)

    async def route(self, message_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        message_id = f"msg-{uuid.uuid4().hex[:10]}"
        handler = self._handlers.get(message_type)
        if handler is None:
            result: dict[str, Any] = {"ok": False, "error": f"no handler for message type {message_type!r}"}
        else:
            try:
                outcome = handler(payload or {})
                if inspect.isawaitable(outcome):
                    outcome = await outcome
                if isinstance(outcome, dict):
                    result = {"ok": True, "result": outcome}
                else:
                    result = {"ok": True, "result": {"value": outcome}}
            except Exception as exc:  # noqa: BLE001
                result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        self._history.append(
            {"message_id": message_id, "type": message_type, "ok": result.get("ok", False)}
        )
        return {"message_id": message_id, "type": message_type, **result}

    def history(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._history[-limit:])

    def snapshot(self) -> dict[str, Any]:
        return {"message_types": self.types(), "messages_routed": len(self._history)}
