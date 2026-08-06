"""Deterministic, clock-driven job scheduler (no real threads or time)."""
from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Job", "Scheduler"]


@dataclass(slots=True)
class Job:
    """A scheduled job; ``interval_seconds`` of 0 means run every tick."""

    name: str
    interval_seconds: float = 0.0
    due_at: float = 0.0
    runs: int = 0


class Scheduler:
    """Simulated scheduler advanced explicitly via :meth:`tick`.

    The internal clock starts at 0. Jobs with a positive interval are first
    due at ``interval_seconds``; one-shot jobs (interval 0) are due on every
    tick. Everything is deterministic and free of real time.
    """

    def __init__(self) -> None:
        self._clock: float = 0.0
        self._jobs: dict[str, Job] = {}

    def register(self, name: str, interval_seconds: float = 0.0) -> Job:
        """Register a job (overwrites an existing one of the same name)."""
        job = Job(
            name=name,
            interval_seconds=float(interval_seconds),
            due_at=float(interval_seconds),
        )
        self._jobs[name] = job
        return job

    def unregister(self, name: str) -> bool:
        """Remove a job; returns whether it was registered."""
        return self._jobs.pop(name, None) is not None

    def names(self) -> list[str]:
        return list(self._jobs)

    def clock(self) -> float:
        return self._clock

    def due(self) -> list[str]:
        """Names of jobs due at the current clock, in registration order."""
        return [name for name, job in self._jobs.items() if job.due_at <= self._clock]

    def next_run(self, name: str) -> float | None:
        job = self._jobs.get(name)
        return job.due_at if job is not None else None

    def tick(self, step: float = 1.0) -> list[str]:
        """Advance the clock and run every job that became due."""
        self._clock += float(step)
        due_names = [
            name for name, job in self._jobs.items() if job.due_at <= self._clock
        ]
        for name in due_names:
            job = self._jobs[name]
            job.runs += 1
            if job.interval_seconds > 0:
                job.due_at += job.interval_seconds
        return due_names
