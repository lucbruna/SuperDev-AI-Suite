"""Synchronization job records."""

from __future__ import annotations

import time
import uuid
from typing import Any


class SyncJob:
    """Represents a single synchronization job between two systems."""

    def __init__(self, source: str, target: str, direction: str = "source->target",
                 entity: str = "records") -> None:
        self.job_id = str(uuid.uuid4())
        self.source = source
        self.target = target
        self.direction = direction
        self.entity = entity
        self.status = "pending"
        self.created_at = time.time()
        self.completed_at: float | None = None
        self.records_processed = 0
        self.records_synced = 0
        self.errors: list[str] = []

    def start(self) -> None:
        self.status = "running"

    def finish(self, synced: int) -> None:
        self.records_processed = synced
        self.records_synced = synced
        self.status = "completed"
        self.completed_at = time.time()

    def fail(self, error: str) -> None:
        self.status = "failed"
        self.errors.append(error)
        self.completed_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "source": self.source,
            "target": self.target,
            "direction": self.direction,
            "entity": self.entity,
            "status": self.status,
            "records_synced": self.records_synced,
            "errors": list(self.errors),
        }
