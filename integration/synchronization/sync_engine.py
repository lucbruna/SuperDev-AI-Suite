"""Synchronization engine: facade over jobs, deltas, conflicts, and history."""

from __future__ import annotations

import logging
from typing import Any, Callable

from .conflict_resolver import ConflictResolver
from .delta_tracker import DeltaTracker
from .history import SyncHistory
from .schedule import SyncScheduler
from .sync_job import SyncJob


class SynchronizationEngine:
    """Facade for the synchronization subsystem."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.synchronization")
        self.deltas = DeltaTracker()
        self.conflicts = ConflictResolver()
        self.history = SyncHistory()
        self.scheduler = SyncScheduler()

    def sync(self, source: str, target: str, records: list[dict[str, Any]],
             entity: str = "records") -> dict[str, Any]:
        """Runs a one-shot sync from source to target, resolving conflicts."""
        job = SyncJob(source, target, entity=entity)
        job.start()
        synced = 0
        for record in records:
            key = record.get("id", record.get("key"))
            if key is None:
                job.fail(f"record without id: {record!r}")
                continue
            if not self.deltas.has_changes_since(source, record.get("updated_at", key)):
                continue
            resolved = self.conflicts.resolve(
                record,
                {"id": key, "updated_at": record.get("updated_at", 0)},
            )
            if resolved:
                synced += 1
            self.deltas.set_watermark(source, record.get("updated_at", key))
        if job.errors:
            job.fail("; ".join(job.errors[:1]))
        else:
            job.finish(synced)
        self.history.record(job)
        return job.to_dict()

    def schedule(self, job_id: str, callback: Callable[[], Any],
                 interval: float = 60.0) -> None:
        self.scheduler.register(job_id, callback, interval)

    def stats(self) -> dict[str, Any]:
        return {
            "jobs": len(self.history.list()),
            "completed": self.history.count("completed"),
            "failed": self.history.count("failed"),
            "watermarks": len(self.deltas.sources()),
        }
