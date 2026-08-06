"""Scheduler: tick-based, deterministic job scheduling (no clock)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(slots=True)
class ScheduledJob:
    """A job executed every ``interval`` ticks."""

    name: str
    interval: int
    fn: Callable[[], Any] | None = None
    remaining: int = 0

    def ready(self) -> bool:
        return self.remaining <= 0

    def reset(self) -> None:
        self.remaining = self.interval


class SchedulerEngine:
    """Deterministic tick-driven scheduler."""

    def __init__(self) -> None:
        self._jobs: dict[str, ScheduledJob] = {}

    def register(self, job: ScheduledJob) -> None:
        job.remaining = job.interval
        self._jobs[job.name] = job

    def unregister(self, name: str) -> None:
        self._jobs.pop(name, None)

    def tick(self) -> list[tuple[str, Any]]:
        outputs: list[tuple[str, Any]] = []
        for name in sorted(self._jobs):
            job = self._jobs[name]
            job.remaining -= 1
            if job.remaining <= 0:
                output = job.fn() if job.fn is not None else None
                outputs.append((name, output))
                job.reset()
        return outputs

    def names(self) -> list[str]:
        return sorted(self._jobs)
