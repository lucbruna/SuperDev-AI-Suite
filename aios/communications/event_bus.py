"""AIOS Event Bus — topic-based publish/subscribe.

Handlers subscribe by exact event type or wildcard prefix ("aios.*").
Delivery is sequential and awaited; a bounded history is kept for
introspection. Pure in-memory; a broker-backed adapter may replace it.
"""

from __future__ import annotations

import fnmatch
import inspect
import time
import uuid
from typing import Any, Awaitable, Callable

Handler = Callable[[Any], Awaitable[Any] | Any]


class EventBus:
    """In-memory pub/sub event bus with wildcard support."""

    def __init__(self, history_limit: int = 500) -> None:
        self._handlers: dict[str, list[tuple[str, Handler]]] = {}
        self._history: list[dict[str, Any]] = []
        self._history_limit = history_limit

    def subscribe(self, event_type: str, handler: Handler, handler_id: str | None = None) -> str:
        """Subscribe ``handler`` to ``event_type`` (supports '*' wildcards)."""
        hid = handler_id or f"sub-{uuid.uuid4().hex[:10]}"
        self._handlers.setdefault(event_type, []).append((hid, handler))
        return hid

    def unsubscribe(self, handler_id: str) -> bool:
        for event_type, subs in self._handlers.items():
            before = len(subs)
            subs[:] = [s for s in subs if s[0] != handler_id]
            if len(subs) < before:
                return True
        return False

    def subscriptions(self, event_type: str) -> list[str]:
        return [hid for hid, _ in self._handlers.get(event_type, [])]

    async def publish(self, event: Any) -> dict[str, Any]:
        """Deliver an event to matching subscribers; record history."""
        event_type = getattr(event, "type", None) or (event.get("type") if isinstance(event, dict) else None)
        event_id = getattr(event, "event_id", None) or f"evt-{uuid.uuid4().hex[:10]}"
        delivered = 0
        errors: list[str] = []
        for pattern, subs in list(self._handlers.items()):
            if not fnmatch.fnmatch(event_type or "", pattern):
                continue
            for hid, handler in list(subs):
                try:
                    result = handler(event)
                    if inspect.isawaitable(result):
                        await result
                    delivered += 1
                except Exception as exc:  # noqa: BLE001 - subscriber isolation
                    errors.append(f"{hid}: {type(exc).__name__}: {exc}")
        self._history.append(
            {"event_id": event_id, "type": event_type, "delivered": delivered, "timestamp": time.time()}
        )
        if len(self._history) > self._history_limit:
            self._history = self._history[-self._history_limit:]
        return {"ok": True, "event_id": event_id, "type": event_type, "delivered": delivered, "errors": errors}

    def history(self, event_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        items = self._history
        if event_type is not None:
            items = [h for h in items if h["type"] == event_type]
        return list(items[-limit:])

    def snapshot(self) -> dict[str, Any]:
        return {
            "patterns": sorted(self._handlers.keys()),
            "subscription_count": sum(len(s) for s in self._handlers.values()),
            "history": len(self._history),
        }
