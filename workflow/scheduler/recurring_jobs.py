from __future__ import annotations

import time
import uuid
from typing import Any, Callable


class RecurringJobs:
    """Manages recurring job schedules."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}

    def schedule(self, interval: float, action: Callable[..., Any]) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "interval": interval,
            "last_run": 0.0,
            "action": action,
            "paused": False,
        }
        return job_id

    def cancel(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None

    def pause(self, job_id: str) -> None:
        if job_id in self._jobs:
            self._jobs[job_id]["paused"] = True

    def resume(self, job_id: str) -> None:
        if job_id in self._jobs:
            self._jobs[job_id]["paused"] = False

    def tick(self, now: float | None = None) -> None:
        now = now or time.time()
        for job_id, job in list(self._jobs.items()):
            if not job["paused"] and now - job["last_run"] >= job["interval"]:
                job["action"]()
                job["last_run"] = now
