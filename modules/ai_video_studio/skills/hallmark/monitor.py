"""Hallmark monitor — track events and produce a run summary."""
from __future__ import annotations
from typing import Any


class RunMonitor:
    """Record events and summarize the run in progress."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def track(self, event: str, **detail: Any) -> None:
        self.events.append({"event": event, **detail})

    def summary(self) -> dict[str, Any]:
        """Return counts and a roll-up of the tracked events."""
        by_event: dict[str, int] = {}
        for entry in self.events:
            by_event[entry["event"]] = by_event.get(entry["event"], 0) + 1
        return {"events": len(self.events), "by_event": by_event}
