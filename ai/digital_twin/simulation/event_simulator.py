"""Event simulator."""

from __future__ import annotations

from typing import Any


class EventSimulator:
    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []
        self._schedule: list[dict[str, Any]] = []

    def schedule(
        self, event_type: str, time_step: int, data: dict[str, Any] = None, priority: int = 0
    ) -> dict[str, Any]:
        event = {
            "type": event_type,
            "time_step": time_step,
            "data": data or {},
            "priority": priority,
            "status": "scheduled",
        }
        self._schedule.append(event)
        self._schedule.sort(key=lambda e: (e["time_step"], -e["priority"]))
        return event

    def run(self, max_steps: int = 100) -> list[dict[str, Any]]:
        executed = []
        remaining = []
        for event in self._schedule:
            if event["time_step"] <= max_steps:
                event["status"] = "executed"
                executed.append(event)
                self._events.append(event)
            else:
                remaining.append(event)
        self._schedule = remaining
        return executed

    def cancel(self, event_type: str = "", time_step: int = -1) -> int:
        original = len(self._schedule)
        if event_type and time_step >= 0:
            self._schedule = [
                e for e in self._schedule if not (e["type"] == event_type and e["time_step"] == time_step)
            ]
        elif event_type:
            self._schedule = [e for e in self._schedule if e["type"] != event_type]
        return original - len(self._schedule)

    def get_executed(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._events[-limit:]

    def pending_count(self) -> int:
        return len(self._schedule)

    def executed_count(self) -> int:
        return len(self._events)
