"""Async event bus — publish/subscribe for pipeline and studio lifecycle events."""
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Awaitable, Callable

EventHandler = Callable[[str, dict[str, Any]], Awaitable[None]]


@dataclass
class EventRecord:
    event_type: str
    payload: dict[str, Any]
    ts: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class EventBus:
    """Async pub/sub bus with a bounded ring-buffer history for introspection."""

    def __init__(self, max_history: int = 200) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
        self._history: deque[EventRecord] = deque(maxlen=max_history)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register ``handler`` for ``event_type`` (or "*" for all events)."""
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        try:
            self._subscribers[event_type].remove(handler)
        except ValueError:
            pass

    async def publish(self, event_type: str, **payload: Any) -> int:
        """Dispatch to matching handlers (exact type + wildcard). Returns fan-out count."""
        record = EventRecord(event_type=event_type, payload=payload)
        self._history.append(record)
        handlers = list(self._subscribers.get(event_type, ()))
        handlers += list(self._subscribers.get("*", ()))
        for handler in handlers:
            try:
                await handler(event_type, payload)
            except Exception:  # noqa: BLE001 — bus must never break publishers
                continue
        return len(handlers)

    def history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Most-recent events, newest first."""
        return [
            {"ts": r.ts, "event": r.event_type, "payload": r.payload}
            for r in list(self._history)[-limit:][::-1]
        ]

    def subscriber_count(self, event_type: str | None = None) -> int:
        if event_type is None:
            return sum(len(h) for h in self._subscribers.values())
        return len(self._subscribers.get(event_type, ()))


_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Process-wide singleton bus."""
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus
