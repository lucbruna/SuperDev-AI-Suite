"""Computes upcoming runs for scheduled jobs."""

from __future__ import annotations

from datetime import datetime, timedelta

from automation.scheduler.scheduler_calendar import SchedulerCalendar
from automation.scheduler.scheduler_models import SchedulerJob
from automation.scheduler.scheduler_parser import CronParser


class SchedulerPlanner:
    """Determines when jobs should fire next."""

    def __init__(self, calendar: SchedulerCalendar | None = None) -> None:
        self.calendar = calendar or SchedulerCalendar()

    def next_run(self, job: SchedulerJob,
                 after: datetime | None = None) -> datetime | None:
        anchor = after or datetime.now()
        if job.cron:
            return CronParser(job.cron).next_after(anchor)
        if job.interval_seconds is not None:
            base = job.last_run if job.last_run else anchor.timestamp()
            candidate = datetime.fromtimestamp(base) + timedelta(
                seconds=job.interval_seconds)
            while candidate <= anchor:
                candidate += timedelta(seconds=job.interval_seconds)
            return candidate
        return None

    def next_runs(self, job: SchedulerJob, count: int = 5,
                  after: datetime | None = None) -> list[datetime]:
        runs: list[datetime] = []
        anchor = after or datetime.now()
        for _ in range(count):
            nxt = self.next_run(job, after=anchor)
            if nxt is None:
                break
            runs.append(nxt)
            anchor = nxt + timedelta(seconds=1)
        return runs
