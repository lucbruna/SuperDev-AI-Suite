from __future__ import annotations

import calendar
import datetime
from typing import Any, Callable


class CronParser:
    """Parses and registers cron expressions."""

    def __init__(self) -> None:
        self._jobs: list[dict[str, Any]] = []

    def register(self, expression: str, action: Callable[..., Any]) -> None:
        parts = expression.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {expression!r}")
        self._jobs.append({
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "day_of_week": parts[4],
            "action": action,
        })

    def _matches(self, field: str, value: int) -> bool:
        return field == "*" or str(value) in field.split(",")

    def tick(self, now: datetime.datetime | None = None) -> None:
        now = now or datetime.datetime.now()
        for job in self._jobs:
            if (
                self._matches(job["minute"], now.minute)
                and self._matches(job["hour"], now.hour)
                and self._matches(job["day"], now.day)
                and self._matches(job["month"], now.month)
                and self._matches(job["day_of_week"], now.weekday())
            ):
                job["action"]()
