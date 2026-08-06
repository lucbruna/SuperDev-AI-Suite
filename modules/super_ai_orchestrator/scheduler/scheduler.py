"""PeriodicScheduler — deterministic, tick-based scheduling.

The scheduler has no clock. It advances an internal tick counter and fires
jobs whose interval has elapsed. When a job fires, the task produced by its
builder is passed to the registered ``submit_fn`` (usually wired to the
kernel's ``submit``). If no ``submit_fn`` is registered the fired task is
recorded in ``fired`` for inspection — graceful degradation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from modules.super_ai_orchestrator.core.task import Task

TaskBuilder = Callable[[], Task]
SubmitFn = Callable[[Task], Any]


@dataclass(slots=True)
class Job:
    """A periodic job.

    Attributes:
        name: unique job name.
        interval_ticks: fire every N ticks.
        builder: produces the task to submit on each fire.
        last_fired_tick: tick of the last fire (-1 = never).
        enabled: whether the job is active.
    """

    name: str
    interval_ticks: int
    builder: TaskBuilder
    last_fired_tick: int = -1
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "interval_ticks": self.interval_ticks,
            "last_fired_tick": self.last_fired_tick,
            "enabled": self.enabled,
        }


class PeriodicScheduler:
    """Deterministic periodic scheduler driven by an explicit tick counter.

    Attributes:
        tick_counter: current tick number.
        submit_fn: callable receiving each fired task (or None).
        fired: tasks fired while no submit_fn was registered.
    """

    def __init__(self, submit_fn: SubmitFn | None = None) -> None:
        self.submit_fn = submit_fn
        self.tick_counter = 0
        self._jobs: dict[str, Job] = {}
        self.fired: list[Task] = []

    def add(
        self,
        name: str,
        interval_ticks: int,
        builder: TaskBuilder,
    ) -> Job:
        """Register a periodic job (interval must be >= 1)."""
        if interval_ticks < 1:
            raise ValueError("interval_ticks must be >= 1")
        if name in self._jobs:
            raise ValueError(f"job '{name}' already registered")
        # Anchor at the current tick: a job with interval N fires exactly
        # on the N-th tick after registration.
        job = Job(
            name=name,
            interval_ticks=interval_ticks,
            builder=builder,
            last_fired_tick=self.tick_counter,
        )
        self._jobs[name] = job
        return job

    def remove(self, name: str) -> bool:
        """Remove a job; returns True if it existed."""
        return self._jobs.pop(name, None) is not None

    def pause(self, name: str) -> bool:
        job = self._jobs.get(name)
        if job is None:
            return False
        job.enabled = False
        return True

    def resume(self, name: str) -> bool:
        job = self._jobs.get(name)
        if job is None:
            return False
        job.enabled = True
        return True

    def tick(self, steps: int = 1) -> list[Task]:
        """Advance the counter and fire due jobs.

        Returns:
            The list of tasks fired during this advance.
        """
        fired_tasks: list[Task] = []
        for _ in range(steps):
            self.tick_counter += 1
            for job in self._jobs.values():
                if not job.enabled:
                    continue
                if self.tick_counter - job.last_fired_tick >= job.interval_ticks:
                    job.last_fired_tick = self.tick_counter
                    task = job.builder()
                    fired_tasks.append(task)
                    if self.submit_fn is not None:
                        self.submit_fn(task)
                    else:
                        self.fired.append(task)
        return fired_tasks

    def jobs(self) -> tuple[Job, ...]:
        return tuple(self._jobs.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick": self.tick_counter,
            "jobs": [j.to_dict() for j in self._jobs.values()],
        }
