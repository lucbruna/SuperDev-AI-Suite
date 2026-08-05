"""Voice Scheduler — priority queue that batches synthesis jobs."""
from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Any

from modules.ai_video_studio.ai_voice_studio.voice_engine import get_voice_engine

_SCHEDULER = None


def get_voice_scheduler() -> VoiceScheduler:
    global _SCHEDULER
    if _SCHEDULER is None:
        _SCHEDULER = VoiceScheduler()
    return _SCHEDULER


class VoiceScheduler:
    """Small async priority scheduler for synthesis jobs.

    Lower ``priority`` numbers run first. Jobs are plain dicts so this stays
    engine-agnostic; the engine is invoked through the shared instance.
    """

    def __init__(self, max_queue: int = 256) -> None:
        self.max_queue = max_queue
        self._queues: dict[int, deque[dict[str, Any]]] = {}
        self._pending: dict[str, dict[str, Any]] = {}
        self._worker: asyncio.Task | None = None
        self.engine = get_voice_engine()

    def submit(self, job: dict[str, Any]) -> str:
        job_id = job.get("id") or f"voice_{int(time.time() * 1000)}"
        priority = int(job.get("priority", 5))
        self._queues.setdefault(priority, deque()).append({**job, "id": job_id})
        self._pending[job_id] = {"status": "queued", "priority": priority}
        return job_id

    def status(self, job_id: str) -> dict[str, Any] | None:
        return self._pending.get(job_id)

    async def run(self) -> None:
        """Consume the queues until empty (used by a background worker)."""
        while self._has_work():
            priority = min(self._queues.keys())
            queue = self._queues[priority]
            job = queue.popleft()
            if not queue:
                del self._queues[priority]
            self._pending[job["id"]]["status"] = "processing"
            try:
                result = await self.engine.synthesize_async(
                    job["text"],
                    voice_id=job.get("voice_id", "default"),
                    language=job.get("language", "en"),
                    emotion=job.get("emotion"),
                    speed=float(job.get("speed", 1.0)),
                    pitch=float(job.get("pitch", 1.0)),
                )
                self._pending[job["id"]].update({"status": "completed", "result": result})
            except Exception as e:  # noqa: BLE001
                self._pending[job["id"]].update({"status": "failed", "error": str(e)})

    def _has_work(self) -> bool:
        return any(q for q in self._queues.values())
