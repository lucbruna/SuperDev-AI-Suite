"""TimeScheduler: earliest/latest-start scheduling with slack over a task DAG."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScheduleEntry:
    task_id: str
    start: float
    end: float
    slack: float
    duration: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "start": self.start,
            "end": self.end,
            "slack": self.slack,
            "duration": self.duration,
        }


class TimeScheduler:
    """Deterministic earliest-start scheduling.

    ``durations`` must cover every task id in ``order``; the schedule is
    computed purely from durations and dependency structure.
    """

    def schedule(
        self,
        order: list[str],
        dependencies: dict[str, list[str]],
        durations: dict[str, float],
        t0: float = 0.0,
    ) -> dict[str, ScheduleEntry]:
        missing = [tid for tid in order if tid not in durations]
        if missing:
            raise ValueError(f"missing durations for task(s): {missing}")

        durs = {tid: max(0.0, float(durations[tid])) for tid in order}
        dependents: dict[str, list[str]] = {tid: [] for tid in order}
        for tid in order:
            for dep in dependencies.get(tid, []):
                if dep not in dependents:
                    raise ValueError(f"dependency {dep!r} of {tid!r} is not part of the workflow")
                dependents[dep].append(tid)

        # Forward pass: earliest start = max end of dependencies.
        earliest_start: dict[str, float] = {}
        earliest_end: dict[str, float] = {}
        for tid in order:
            deps = [d for d in dependencies.get(tid, []) if d in durs]
            earliest_start[tid] = t0 if not deps else max(earliest_end[d] for d in deps)
            earliest_end[tid] = earliest_start[tid] + durs[tid]
        total = max(earliest_end.values(), default=t0)

        # Reverse pass: latest end = min start of dependents.
        latest_start: dict[str, float] = {}
        latest_end: dict[str, float] = {}
        for tid in reversed(order):
            if not dependents[tid]:
                latest_end[tid] = total
            else:
                latest_end[tid] = min(latest_start[d] for d in dependents[tid])
            latest_start[tid] = latest_end[tid] - durs[tid]

        return {
            tid: ScheduleEntry(
                task_id=tid,
                start=round(earliest_start[tid], 6),
                end=round(earliest_end[tid], 6),
                slack=round(latest_start[tid] - earliest_start[tid], 6),
                duration=durs[tid],
            )
            for tid in order
        }
