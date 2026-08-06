"""Event model and bus for the Digital Twin module.

Deterministic: events carry a monotonically increasing sequence number and
are dispatched synchronously. No wall-clock dependency.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

EventHandler = Callable[["TwinEvent"], None]


@dataclass(slots=True)
class TwinEvent:
    """A single event produced by the twin runtime."""

    type: str
    payload: dict[str, object] = field(default_factory=dict)
    sequence: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.type,
            "payload": self.payload,
            "sequence": self.sequence,
        }


class TwinEventBus:
    """Synchronous publish/subscribe bus with an append-only history."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._history: list[TwinEvent] = []
        self._sequence = 0

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event_type: str, payload: dict[str, object] | None = None) -> TwinEvent:
        self._sequence += 1
        event = TwinEvent(type=event_type, payload=payload or {}, sequence=self._sequence)
        self._history.append(event)
        for handler in list(self._subscribers.get(event_type, [])):
            handler(event)
        return event

    def history(self) -> list[TwinEvent]:
        return list(self._history)

    def history_of(self, event_type: str) -> list[TwinEvent]:
        return [e for e in self._history if e.type == event_type]

    def clear(self) -> None:
        self._history.clear()
        self._sequence = 0

    @property
    def last_sequence(self) -> int:
        return self._sequence
