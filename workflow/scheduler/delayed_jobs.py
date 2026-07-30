from __future__ import annotations

import time
import uuid
from typing import Any, Callable


class DelayedJobs:
    """Manages one-shot delayed job executions."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}

    def schedule(self, delay: float, action: Callable[..., Any]) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "run_at": time.time() + delay,
            "action": action,
            "fired": False,
        }
        return job_id

    def cancel(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None

    def tick(self, now: float | None = None) -> None:
        now = now or time.time()
        for job_id, job in list(self._jobs.items()):
            if not job["fired"] and now >= job["run_at"]:
                job["action"]()
                job["fired"] = True
                del self._jobs[job_id]
