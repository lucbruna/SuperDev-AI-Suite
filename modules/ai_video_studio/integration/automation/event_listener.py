"""Event Listener — records studio event-bus traffic for automation rules."""
from __future__ import annotations

from typing import Any


class EventListener:
    """Tracks event types observed (fed by the studio event bus)."""

    def __init__(self) -> None:
        self._observed: dict[str, int] = {}

    def observe(self, event_type: str) -> None:
        self._observed[event_type] = self._observed.get(event_type, 0) + 1

    def list(self) -> dict[str, Any]:
        return {"observed": dict(self._observed), "count": len(self._observed)}


_event_listener: EventListener | None = None


def get_event_listener() -> EventListener:
    global _event_listener
    if _event_listener is None:
        _event_listener = EventListener()
    return _event_listener
