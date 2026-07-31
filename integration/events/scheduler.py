"""Event scheduler for delayed and recurring emissions."""

from __future__ import annotations

import time
from typing import Any, Callable

from .event_bus import EventBus


class EventScheduler:
    """Schedules one-shot and recurring event emissions."""

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus
        self._jobs: dict[str, dict[str, Any]] = {}

    def schedule(self, job_id: str, event_type: str, payload: dict[str, Any],
                 delay: float = 0.0, interval: float | None = None) -> None:
        self._jobs[job_id] = {
            "event_type": event_type,
            "payload": payload,
            "run_at": time.time() + delay,
            "interval": interval,
            "next": time.time() + delay,
            "fired": 0,
        }

    def run_due(self) -> int:
        now = time.time()
        fired = 0
        for job_id, job in list(self._jobs.items()):
            if now < job["next"]:
                continue
            self._bus.publish(job["event_type"], dict(job["payload"]))
            job["fired"] += 1
            fired += 1
            if job["interval"]:
                job["next"] = now + job["interval"]
            else:
                self._jobs.pop(job_id, None)
        return fired

    def cancel(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None

    def jobs(self) -> dict[str, int]:
        return {jid: j["fired"] for jid, j in self._jobs.items()}
