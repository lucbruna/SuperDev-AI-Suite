from __future__ import annotations

import logging
from typing import Any, Callable


class EventStream:
    """In-memory pub/sub event stream for realtime channels."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.realtime.events")
        self._subscribers: dict[str, list[Callable[[str, Any], None]]] = {}
        self._history: list[dict[str, Any]] = []

    def subscribe(self, channel: str, handler: Callable[[str, Any], None]) -> None:
        self._subscribers.setdefault(channel, []).append(handler)

    def unsubscribe(self, channel: str, handler: Callable[[str, Any], None]) -> None:
        if channel in self._subscribers:
            try:
                self._subscribers[channel].remove(handler)
            except ValueError:
                pass

    def publish(self, channel: str, data: Any) -> None:
        self._history.append({"channel": channel, "data": data})
        for handler in list(self._subscribers.get(channel, [])):
            handler(channel, data)

    def subscriber_count(self) -> dict[str, int]:
        return {channel: len(handlers) for channel, handlers in self._subscribers.items()}

    def history(self, channel: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        events = self._history
        if channel is not None:
            events = [e for e in events if e["channel"] == channel]
        if limit is not None:
            events = events[-limit:]
        return list(events)

    def clear(self) -> None:
        self._history.clear()
