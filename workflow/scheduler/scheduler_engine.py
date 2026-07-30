from __future__ import annotations

import logging
import time
from typing import Any, Callable

from .cron import CronParser
from .interval import IntervalScheduler
from .delayed_jobs import DelayedJobs
from .recurring_jobs import RecurringJobs


class SchedulerEngine:
    """Central engine for scheduling workflow executions."""

    def __init__(self) -> None:
        self._cron = CronParser()
        self._interval = IntervalScheduler()
        self._delayed = DelayedJobs()
        self._recurring = RecurringJobs()
        self._log = logging.getLogger("superdev.workflow.scheduler")

    def schedule_cron(self, expression: str, action: Callable[..., Any]) -> None:
        self._cron.register(expression, action)

    def schedule_interval(self, seconds: float, action: Callable[..., Any]) -> str:
        return self._interval.schedule(seconds, action)

    def schedule_delayed(self, delay: float, action: Callable[..., Any]) -> str:
        return self._delayed.schedule(delay, action)

    def schedule_recurring(self, interval: float, action: Callable[..., Any]) -> str:
        return self._recurring.schedule(interval, action)

    def cancel(self, job_id: str) -> bool:
        return (
            self._interval.cancel(job_id)
            or self._delayed.cancel(job_id)
            or self._recurring.cancel(job_id)
        )

    def tick(self) -> None:
        self._delayed.tick()
        self._interval.tick()
        self._recurring.tick()
