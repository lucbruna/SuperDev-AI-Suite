"""Synchronization history log."""

from __future__ import annotations

from typing import Any

from .sync_job import SyncJob


class SyncHistory:
    """Stores past synchronization job results."""

    def __init__(self) -> None:
        self._jobs: list[SyncJob] = []

    def record(self, job: SyncJob) -> None:
        self._jobs.append(job)

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return [j.to_dict() for j in self._jobs[-limit:]]

    def count(self, status: str | None = None) -> int:
        if status is None:
            return len(self._jobs)
        return sum(1 for j in self._jobs if j.status == status)

    def failures(self) -> list[dict[str, Any]]:
        return [j.to_dict() for j in self._jobs if j.status == "failed"]

    def clear(self) -> None:
        self._jobs.clear()
