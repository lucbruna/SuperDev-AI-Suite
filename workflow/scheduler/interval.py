from __future__ import annotations

import time
import uuid
from typing import Any, Callable


class IntervalScheduler:
    """Schedules actions at fixed intervals."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}

    def schedule(self, seconds: float, action: Callable[..., Any]) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "interval": seconds,
            "last_run": 0.0,
            "action": action,
        }
        return job_id

    def cancel(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None

    def tick(self, now: float | None = None) -> None:
        now = now or time.time()
        for job_id, job in list(self._jobs.items()):
            if now - job["last_run"] >= job["interval"]:
                job["action"]()
                job["last_run"] = now
