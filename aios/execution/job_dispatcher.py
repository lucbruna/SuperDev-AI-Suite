"""JobDispatcher: queue and lifecycle tracking for execution jobs."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional

JOB_STATUSES = ("pending", "ready", "running", "completed", "failed", "cancelled")


@dataclass
class Job:
    job_id: str
    task_id: str
    name: str = ""
    status: str = "pending"
    attempts: int = 0
    result: Any = None
    error: Optional[str] = None
    params: dict[str, Any] = field(default_factory=dict)
    agent: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class JobDispatcher:
    """In-memory job registry with deterministic sequential ids."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._seq = 0

    def submit(self, task: Any = None, name: str | None = None, params: dict[str, Any] | None = None, agent: str | None = None) -> Job:
        self._seq += 1
        job_id = f"job-{self._seq:04d}"
        job = Job(
            job_id=job_id,
            task_id=getattr(task, "task_id", job_id),
            name=name or getattr(task, "name", ""),
            params=dict(params or getattr(task, "params", {})),
            agent=agent or getattr(task, "agent", None),
        )
        self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def jobs(self) -> list[Job]:
        return [self._jobs[job_id] for job_id in sorted(self._jobs)]

    def by_status(self, status: str) -> list[Job]:
        return [job for job in self.jobs() if job.status == status]

    def mark(self, job_id: str, status: str, result: Any = None, error: BaseException | None = None) -> Optional[Job]:
        if status not in JOB_STATUSES:
            raise ValueError(f"invalid job status {status!r}; expected one of {JOB_STATUSES}")
        job = self._jobs.get(job_id)
        if job is None:
            return None
        job.status = status
        if result is not None or status == "completed":
            job.result = result
        if error is not None:
            job.error = str(error)
        return job

    def cancel(self, job_id: str) -> Optional[Job]:
        return self.mark(job_id, "cancelled")

    def stats(self) -> dict[str, int]:
        counts: dict[str, int] = {status: 0 for status in JOB_STATUSES}
        for job in self._jobs.values():
            counts[job.status] = counts.get(job.status, 0) + 1
        counts["total"] = len(self._jobs)
        return counts
