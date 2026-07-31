"""Synchronization scheduling."""

from __future__ import annotations

import time
from typing import Any, Callable


class SyncScheduler:
    """Runs sync jobs on an interval basis."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}

    def register(self, job_id: str, callback: Callable[[], Any],
                 interval: float = 60.0) -> None:
        self._jobs[job_id] = {
            "callback": callback,
            "interval": interval,
            "next": time.time() + interval,
            "runs": 0,
        }

    def run_due(self) -> list[str]:
        now = time.time()
        ran: list[str] = []
        for job_id, job in list(self._jobs.items()):
            if now < job["next"]:
                continue
            job["callback"]()
            job["runs"] += 1
            job["next"] = now + job["interval"]
            ran.append(job_id)
        return ran

    def unregister(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None

    def runs(self, job_id: str) -> int:
        return self._jobs.get(job_id, {}).get("runs", 0)

    def next_run(self, job_id: str) -> float | None:
        return self._jobs.get(job_id, {}).get("next")
