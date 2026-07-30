from __future__ import annotations

from workflow.scheduler.cron import CronParser
from workflow.scheduler.interval import IntervalScheduler
from workflow.scheduler.delayed_jobs import DelayedJobs
from workflow.scheduler.recurring_jobs import RecurringJobs


class TestScheduler:
    def test_cron_tick(self) -> None:
        calls: list[str] = []
        cron = CronParser()
        cron.register("* * * * *", lambda: calls.append("fired"))
        import datetime
        cron.tick(datetime.datetime(2026, 1, 1, 12, 0))
        assert len(calls) == 1

    def test_interval_tick(self) -> None:
        calls: list[str] = []
        sched = IntervalScheduler()
        sched.schedule(0.01, lambda: calls.append("fired"))
        sched.tick(now=100.0)
        assert len(calls) >= 1

    def test_delayed_jobs(self) -> None:
        calls: list[str] = []
        dj = DelayedJobs()
        dj.schedule(0.01, lambda: calls.append("fired"))
        dj.tick(now=100.0)
        assert len(calls) == 1

    def test_recurring_jobs(self) -> None:
        calls: list[str] = []
        rj = RecurringJobs()
        rj.schedule(0.01, lambda: calls.append("fired"))
        rj.tick(now=100.1)
        rj.tick(now=100.2)
        assert len(calls) == 2
