"""Render queue — priority FIFO queue for export jobs.

Provides a thread-based worker so long encodes (5-10 min videos) don't
block the API, plus ``get_status`` for polling.
"""
from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


JobFn = Callable[[], dict[str, Any]]


@dataclass
class RenderJob:
    """A queued export job."""

    id: str
    name: str
    target: dict[str, Any]
    created_at: float
    status: str = "queued"  # queued | rendering | done | failed
    progress: float = 0.0
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class RenderQueue:
    """Priority FIFO queue with a background worker thread."""

    def __init__(self, output_dir: str | Path, *, workers: int = 1) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._jobs: dict[str, RenderJob] = {}
        self._order: list[str] = []
        self._lock = threading.RLock()
        self._worker: threading.Thread | None = None
        self._stop = False
        self._workers_n = max(1, workers)

    # ── Public API ─────────────────────────────────────────────
    def submit(
        self,
        target: dict[str, Any],
        *,
        name: str | None = None,
        priority: int = 0,
    ) -> str:
        """Queue an export; returns the job id. Higher ``priority`` runs first."""
        job_id = uuid.uuid4().hex[:12]
        job = RenderJob(
            id=job_id,
            name=name or target.get("name", f"job-{job_id[:6]}"),
            target=target,
            created_at=time.time(),
        )
        job.target["_priority"] = priority
        with self._lock:
            self._jobs[job_id] = job
            self._order.append(job_id)
            self._order.sort(
                key=lambda jid: -self._jobs[jid].target.get("_priority", 0)
            )
        self._ensure_worker()
        return job_id

    def get_status(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            job = self._jobs[job_id]
            return {
                "id": job.id,
                "name": job.name,
                "status": job.status,
                "progress": job.progress,
                "error": job.error,
                "result": job.result,
                "created_at": job.created_at,
            }

    def list_jobs(self) -> list[dict[str, Any]]:
        with self._lock:
            return [self.get_status(j) for j in self._order]

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.status == "queued":
                job.status = "failed"
                job.error = "cancelled"
                self._order.remove(job_id)
                return True
            return False

    def shutdown(self) -> None:
        self._stop = True
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=5)

    # ── Internals ──────────────────────────────────────────────
    def _ensure_worker(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        self._stop = False
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _run(self) -> None:
        while not self._stop:
            with self._lock:
                ready = [
                    j for j in self._order
                    if self._jobs[j].status == "queued"
                ]
                if not ready:
                    time.sleep(0.2)
                    continue
                jid = ready[0]
                job = self._jobs[jid]
                job.status = "rendering"
            try:
                target = {k: v for k, v in job.target.items() if k != "_priority"}
                path = self._output_dir / f"{job.name}.{_ext_for(target)}"
                target.setdefault("output_path", path)

                def _on_progress(p: float, done: int, total: int, _jid: str = jid) -> None:
                    with self._lock:
                        self._jobs[_jid].progress = p

                from modules.ai_video_studio.ai_export.export_engine import ExportEngine

                local = ExportEngine(self._output_dir)
                result = local.export_frames(
                    _lazy_frames(target),
                    preset=target.get("preset"),
                    profile=target.get("profile"),
                    fps=target.get("fps"),
                    resolution=target.get("resolution"),
                    output_path=target.get("output_path"),
                    progress=_on_progress,
                )
                with self._lock:
                    job.status = "done"
                    job.progress = 1.0
                    job.result = result
            except Exception as e:  # noqa: BLE001
                with self._lock:
                    job.status = "failed"
                    job.error = str(e)
            finally:
                with self._lock:
                    if jid in self._order:
                        self._order.remove(jid)


_CONTAINER_EXT = {
    "mp4": "mp4",
    "matroska": "mkv",
    "avi": "avi",
    "webm": "webm",
    "mov": "mov",
    "gif": "gif",
    "image2": "png",
}


def _ext_for(target: dict[str, Any]) -> str:
    """Derive a sensible extension from the job target."""
    from modules.ai_video_studio.ai_export.export_presets import PRESETS
    from modules.ai_video_studio.ai_export.export_profiles import PROFILES

    preset = target.get("preset")
    profile = target.get("profile")
    if preset and preset in PRESETS:
        prof_name = PRESETS[preset].profile
        if prof_name in PROFILES:
            return _CONTAINER_EXT.get(PROFILES[prof_name].container, "mp4")
    if profile and profile in PROFILES:
        return _CONTAINER_EXT.get(PROFILES[profile].container, "mp4")
    return "mp4"


def _lazy_frames(target: dict[str, Any]):
    """Yield frames from the target's ``frames`` key, if present."""
    frames = target.get("frames")
    if frames is None:
        raise ValueError("target requires 'frames' for queued rendering")
    yield from frames
