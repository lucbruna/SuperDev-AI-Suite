"""Schedules periodic checks for time-based triggers."""

from __future__ import annotations

import time
from typing import Any

from automation.triggers.trigger_models import TriggerEvent


class TriggerScheduler:
    """Fires time triggers on a fixed interval."""

    def __init__(self, router: Any = None, events: Any = None) -> None:
        self.router = router
        self.events = events
        self._intervals: dict[str, float] = {}
        self._last: dict[str, float] = {}

    def schedule(self, trigger_id: str, interval_seconds: float) -> None:
        self._intervals[trigger_id] = interval_seconds
        self._last.setdefault(trigger_id, 0.0)

    def unschedule(self, trigger_id: str) -> bool:
        if trigger_id in self._intervals:
            del self._intervals[trigger_id]
            self._last.pop(trigger_id, None)
            return True
        return False

    def due(self, now: float | None = None) -> list[str]:
        anchor = now if now is not None else time.time()
        return [trigger_id for trigger_id, interval in self._intervals.items()
                if anchor - self._last[trigger_id] >= interval]

    def run_due(self, now: float | None = None) -> list[str]:
        anchor = now if now is not None else time.time()
        fired: list[str] = []
        for trigger_id in self.due(anchor):
            self._last[trigger_id] = anchor
            fired.append(trigger_id)
            if self.router is not None:
                self.router.route(TriggerEvent("time", {"trigger_id": trigger_id}))
        return fired
