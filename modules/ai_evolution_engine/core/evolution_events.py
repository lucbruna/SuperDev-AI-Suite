"""Synchronous event bus for the AI Evolution Engine."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(slots=True)
class EvolutionEvent:
    """A single event emitted by the engine (synchronous, in-memory)."""

    type: str
    payload: dict[str, object] = field(default_factory=dict)
    sequence: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.type,
            "payload": self.payload,
            "sequence": self.sequence,
        }


class EvolutionEventBus:
    """Records and dispatches events deterministically."""

    def __init__(self) -> None:
        self._history: list[EvolutionEvent] = []
        self._listeners: list[Callable[[EvolutionEvent], None]] = []
        self._sequence = 0

    def publish(self, event_type: str, payload: dict[str, object] | None = None) -> None:
        self._sequence += 1
        event = EvolutionEvent(
            type=event_type,
            payload=payload or {},
            sequence=self._sequence,
        )
        self._history.append(event)
        for listener in list(self._listeners):
            listener(event)

    def subscribe(self, listener: Callable[[EvolutionEvent], None]) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def history(self) -> list[EvolutionEvent]:
        return list(self._history)

    def history_of(self, event_type: str) -> list[EvolutionEvent]:
        return [e for e in self._history if e.type == event_type]

    def clear(self) -> None:
        self._history.clear()
        self._sequence = 0
