"""Executes scheduled jobs."""

from __future__ import annotations

import time
from typing import Any, Callable

from automation.scheduler.scheduler_models import SchedulerJob


class SchedulerExecutor:
    """Runs a job through a configured runner and tracks its last run."""

    def __init__(self,
                 runner: Callable[[str, SchedulerJob], Any] | None = None) -> None:
        # runner(workflow_id, job) -> result
        self.runner = runner

    def run(self, job: SchedulerJob, now: Any = None) -> Any:
        if self.runner is None:
            raise RuntimeError("no runner configured")
        result = self.runner(job.workflow_id, job)
        job.last_run = (now.timestamp() if now else time.time())
        return result
