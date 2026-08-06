"""EventBus — a deterministic, in-process event bus.

Listeners are called synchronously, in subscription order, for every
published event. Every published event is also recorded in the log, so
consumers can replay history in exact order. There is no clock and no
concurrency here: ordering is purely the monotonic ``seq``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from modules.super_ai_orchestrator.events.event import Event

Listener = Callable[[Event], None]


@dataclass(slots=True)
class EventBus:
    """Minimal deterministic event bus.

    Attributes:
        seq: next sequence number to assign.
        log: ordered list of all published events.
        _listeners: ordered subscription list.
    """

    seq: int = 0
    log: list[Event] = field(default_factory=list)
    _listeners: list[Listener] = field(default_factory=list)

    def subscribe(self, listener: Listener) -> Callable[[], None]:
        """Register a listener; returns an unsubscribe callable."""
        self._listeners.append(listener)

        def unsubscribe() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return unsubscribe

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> Event:
        """Publish an event: assign the next seq, record it, notify listeners."""
        event = Event(type=event_type, payload=payload or {}, seq=self.seq)
        self.seq += 1
        self.log.append(event)
        for listener in list(self._listeners):
            listener(event)
        return event

    def history(self, event_type: str | None = None) -> tuple[Event, ...]:
        """All recorded events, optionally filtered by type, in order."""
        if event_type is None:
            return tuple(self.log)
        return tuple(e for e in self.log if e.type == event_type)

    def clear(self) -> None:
        """Reset the bus (log and sequence). Listeners are kept."""
        self.log.clear()
        self.seq = 0
