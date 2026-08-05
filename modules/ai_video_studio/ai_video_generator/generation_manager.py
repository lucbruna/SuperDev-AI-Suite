"""Generation manager — submit and track video generation jobs."""
from __future__ import annotations

import time
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class GenerationManager:
    """Owns the lifecycle of generation jobs (pending → running → done)."""

    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_DONE = "done"
    STATUS_FAILED = "failed"

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}

    def submit(
        self,
        prompt: str,
        *,
        mode: str = "text_to_video",
        model: str | None = None,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        rid = request_id or f"job_{len(self._jobs) + 1}"
        if rid in self._jobs:
            raise ValidationError(f"Job '{rid}' already exists", field="request_id")
        job: dict[str, Any] = {
            "id": rid,
            "mode": mode,
            "prompt": prompt,
            "model": model,
            "params": params or {},
            "status": self.STATUS_PENDING,
            "created_at": time.time(),
            "started_at": None,
            "finished_at": None,
            "output": None,
            "error": None,
        }
        self._jobs[rid] = job
        return self.run(rid)

    def run(self, job_id: str) -> dict[str, Any]:
        job = self._get(job_id)
        job["status"] = self.STATUS_RUNNING
        job["started_at"] = time.time()
        try:
            from modules.ai_video_studio.ai_video_generator.task_dispatcher import get_task_dispatcher

            output = get_task_dispatcher().dispatch(job)
            job["output"] = output
            job["status"] = self.STATUS_DONE
        except Exception as exc:  # noqa: BLE001 — surface any failure as job error
            job["status"] = self.STATUS_FAILED
            job["error"] = str(exc)
        job["finished_at"] = time.time()
        return dict(job)

    def get(self, job_id: str) -> dict[str, Any]:
        return dict(self._get(job_id))

    def cancel(self, job_id: str) -> bool:
        job = self._get(job_id)
        if job["status"] in (self.STATUS_DONE, self.STATUS_FAILED):
            return False
        job["status"] = self.STATUS_FAILED
        job["error"] = "cancelled"
        return True

    def list_jobs(self, status: str | None = None) -> list[dict[str, Any]]:
        jobs = [dict(j) for j in self._jobs.values()]
        if status is not None:
            jobs = [j for j in jobs if j["status"] == status]
        return jobs

    def _get(self, job_id: str) -> dict[str, Any]:
        job = self._jobs.get(job_id)
        if job is None:
            raise ValidationError(f"Job '{job_id}' not found", field="job_id")
        return job


_generation_manager: GenerationManager | None = None


def get_generation_manager() -> GenerationManager:
    global _generation_manager
    if _generation_manager is None:
        _generation_manager = GenerationManager()
    return _generation_manager
