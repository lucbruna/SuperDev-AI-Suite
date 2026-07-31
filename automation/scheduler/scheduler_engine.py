"""Scheduler engine: facade for the scheduler subsystem."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Callable

from automation.automation_events import AutomationEventType
from automation.scheduler.scheduler_executor import SchedulerExecutor
from automation.scheduler.scheduler_models import SchedulerJob
from automation.scheduler.scheduler_planner import SchedulerPlanner


class SchedulerEngine:
    """Registers jobs, computes next runs, and fires due jobs."""

    def __init__(self, planner: SchedulerPlanner | None = None,
                 executor: SchedulerExecutor | None = None,
                 events: Any = None, metrics: Any = None) -> None:
        self.jobs: dict[str, SchedulerJob] = {}
        self._handlers: dict[str, Callable[[], Any]] = {}
        self.planner = planner or SchedulerPlanner()
        self.executor = executor or SchedulerExecutor(self._default_runner)
        self.events = events
        self.metrics = metrics
        self._last_results: list[tuple[str, Any]] = []

    # -- job management ----------------------------------------------------
    def add_job(self, job_id: str, workflow_id: str,
                cron: str | None = None,
                interval_seconds: float | None = None,
                after: datetime | None = None) -> SchedulerJob:
        job = SchedulerJob(job_id=job_id, workflow_id=workflow_id,
                           cron=cron, interval_seconds=interval_seconds)
        first = self.planner.next_run(job, after)
        job.next_run_ts = first.timestamp() if first else None
        self.jobs[job_id] = job
        return job

    def remove_job(self, job_id: str) -> bool:
        return self.jobs.pop(job_id, None) is not None

    def list_jobs(self) -> list[SchedulerJob]:
        return list(self.jobs.values())

    def register_handler(self, workflow_id: str,
                         handler: Callable[[], Any]) -> None:
        self._handlers[workflow_id] = handler

    def next_run(self, job_id: str,
                 after: datetime | None = None) -> datetime | None:
        job = self.jobs.get(job_id)
        if job is None:
            return None
        return self.planner.next_run(job, after)

    def due_jobs(self, now: datetime) -> list[SchedulerJob]:
        return [job for job in self.jobs.values()
                if job.enabled
                and job.next_run_ts is not None
                and datetime.fromtimestamp(job.next_run_ts) <= now]

    def run_due(self, now: datetime | None = None) -> list[tuple[str, Any]]:
        anchor = now or datetime.now()
        results: list[tuple[str, Any]] = []
        for job in self.due_jobs(anchor):
            result = self.executor.run(job, anchor)
            results.append((job.job_id, result))
            self._last_results.append((job.job_id, result))
            nxt = self.planner.next_run(job, after=anchor)
            job.next_run_ts = nxt.timestamp() if nxt else None
            if self.events is not None:
                self.events.publish(AutomationEventType.SCHEDULE_FIRED,
                                    {"job_id": job.job_id,
                                     "workflow_id": job.workflow_id})
            if self.metrics is not None:
                self.metrics.increment("schedules.fired")
        return results

    def last_results(self, limit: int = 20) -> list[tuple[str, Any]]:
        return self._last_results[-limit:]

    def _default_runner(self, workflow_id: str, _job: object) -> Any:
        handler = self._handlers.get(workflow_id)
        if handler is None:
            raise ValueError(f"no handler for workflow '{workflow_id}'")
        return handler()
