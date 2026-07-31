from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TimelineEvent:
    """An event on a timeline."""

    timestamp: float
    label: str
    kind: str = "info"  # info | success | warning | error | milestone
    data: dict[str, Any] = field(default_factory=dict)


class Timeline:
    """Ordered timeline of events."""

    def __init__(self, name: str = "timeline") -> None:
        self.name = name
        self._events: list[TimelineEvent] = []

    def add(self, timestamp: float, label: str, kind: str = "info", **data: Any) -> TimelineEvent:
        event = TimelineEvent(timestamp=timestamp, label=label, kind=kind, data=data)
        self._events.append(event)
        self._events.sort(key=lambda e: e.timestamp)
        return event

    def events(self, reverse: bool = False) -> list[TimelineEvent]:
        events = list(self._events)
        if reverse:
            events.reverse()
        return events

    def by_kind(self, kind: str) -> list[TimelineEvent]:
        return [e for e in self._events if e.kind == kind]

    def span(self) -> tuple[float, float] | None:
        if not self._events:
            return None
        return (self._events[0].timestamp, self._events[-1].timestamp)

    def to_dict(self) -> list[dict[str, Any]]:
        return [vars(e) for e in self._events]
