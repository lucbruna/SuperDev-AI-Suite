from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass
class ReasoningEvent:
    """Event emitted during reasoning operations."""

    event_type: str
    context_id: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReasoningEventBus:
    """Simple event bus for reasoning events."""

    def __init__(self):
        self._handlers: dict[str, list[Callable[[ReasoningEvent], None]]] = {}

    def on(self, event_type: str, handler: Callable[[ReasoningEvent], None]) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def emit(self, event: ReasoningEvent) -> None:
        for handler in self._handlers.get(event.event_type, []):
            handler(event)

    def off(self, event_type: str, handler: Callable[[ReasoningEvent], None]) -> None:
        self._handlers[event_type] = [h for h in self._handlers.get(event_type, []) if h is not handler]
