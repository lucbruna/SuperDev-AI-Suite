"""Publisher Queue — FIFO/priority queue for publish jobs (Volume 7)."""
from __future__ import annotations

import logging
import time
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class PublishStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PublisherQueue:
    """In-memory publish job queue with priority ordering and state machine."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict] = {}

    def enqueue(
        self,
        *,
        content: dict,
        platforms: list[str],
        schedule_at: float | None = None,
        priority: int = 5,
    ) -> dict:
        """Add a publish job to the queue and return its descriptor."""
        job_id = uuid.uuid4().hex[:12]
        job = {
            "job_id": job_id,
            "status": PublishStatus.QUEUED.value,
            "priority": max(1, min(10, int(priority))),
            "platforms": list(platforms),
            "content": content,
            "created_at": time.time(),
            "schedule_at": schedule_at,
            "started_at": None,
            "finished_at": None,
            "results": {},
            "error": None,
        }
        self._jobs[job_id] = job
        logger.info("Enqueued publish job %s for %s", job_id, platforms)
        return job

    def next(self, *, now: float | None = None) -> dict | None:
        """Pop the highest-priority job whose schedule time has arrived."""
        now = now if now is not None else time.time()
        candidates = [
            j for j in self._jobs.values()
            if j["status"] == PublishStatus.QUEUED.value
            and (j["schedule_at"] is None or j["schedule_at"] <= now)
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda j: (-j["priority"], j["created_at"]))
        job = candidates[0]
        job["status"] = PublishStatus.PROCESSING.value
        job["started_at"] = time.time()
        return job

    def mark_published(self, job_id: str, result: dict | None = None) -> dict | None:
        job = self._jobs.get(job_id)
        if not job:
            return None
        job["status"] = PublishStatus.PUBLISHED.value
        job["finished_at"] = time.time()
        if result:
            job["results"] = result
        return job

    def mark_failed(self, job_id: str, error: str) -> dict | None:
        job = self._jobs.get(job_id)
        if not job:
            return None
        job["status"] = PublishStatus.FAILED.value
        job["error"] = error
        job["finished_at"] = time.time()
        return job

    def cancel(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job or job["status"] != PublishStatus.QUEUED.value:
            return False
        job["status"] = PublishStatus.CANCELLED.value
        job["finished_at"] = time.time()
        return True

    def get(self, job_id: str) -> dict | None:
        return self._jobs.get(job_id)

    def list(self, status: str | None = None) -> list[dict]:
        jobs = list(self._jobs.values())
        if status:
            jobs = [j for j in jobs if j["status"] == status]
        return sorted(jobs, key=lambda j: j["created_at"], reverse=True)

    def pending_count(self) -> int:
        return sum(1 for j in self._jobs.values() if j["status"] == PublishStatus.QUEUED.value)

    def stats(self) -> dict[str, int]:
        counts = {s.value: 0 for s in PublishStatus}
        for j in self._jobs.values():
            counts[j["status"]] = counts.get(j["status"], 0) + 1
        counts["total"] = len(self._jobs)
        return counts


_QUEUE: PublisherQueue | None = None


def get_publisher_queue() -> PublisherQueue:
    """Get the module-level singleton queue."""
    global _QUEUE
    if _QUEUE is None:
        _QUEUE = PublisherQueue()
    return _QUEUE
