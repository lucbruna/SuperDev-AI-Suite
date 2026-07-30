from __future__ import annotations

import datetime
from typing import Any, Callable


class SchedulerTrigger:
    """Describes what triggers a scheduled execution."""

    def __init__(self, trigger_type: str, config: dict[str, Any] | None = None) -> None:
        self.trigger_type = trigger_type
        self.config = config or {}

    @classmethod
    def cron(cls, expression: str) -> SchedulerTrigger:
        return cls("cron", {"expression": expression})

    @classmethod
    def interval(cls, seconds: float) -> SchedulerTrigger:
        return cls("interval", {"seconds": seconds})

    @classmethod
    def date(cls, dt: datetime.datetime) -> SchedulerTrigger:
        return cls("date", {"datetime": dt.isoformat()})

    @classmethod
    def event(cls, event_name: str) -> SchedulerTrigger:
        return cls("event", {"event_name": event_name})

    def evaluate(self, context: dict[str, Any] | None = None) -> bool:
        return True  # Subclasses override for conditional logic
