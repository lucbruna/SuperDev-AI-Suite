"""Task dispatcher — route jobs to the correct generation sub-engine."""
from __future__ import annotations

import time
from typing import Any


class TaskDispatcher:
    """Dispatches a generation job to its mode-specific engine."""

    def dispatch(self, job: dict[str, Any]) -> dict[str, Any]:
        mode = job.get("mode", "text_to_video")
        started = time.time()
        try:
            result = self._dispatch(mode, job)
        except Exception as exc:  # noqa: BLE001 — wrap into structured failure
            return {
                "ok": False,
                "mode": mode,
                "error": str(exc),
                "elapsed_seconds": round(time.time() - started, 2),
            }
        result.setdefault("ok", True)
        result.setdefault("elapsed_seconds", round(time.time() - started, 2))
        return result

    def _dispatch(self, mode: str, job: dict[str, Any]) -> dict[str, Any]:
        if mode == "text_to_video":
            from modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine import (
                TextToVideoEngine,
            )

            return TextToVideoEngine().generate(job)
        if mode == "image_to_video":
            from modules.ai_video_studio.ai_video_generator.image_to_video.image_to_video_engine import (
                ImageToVideoEngine,
            )

            return ImageToVideoEngine().generate(job)
        if mode == "video_to_video":
            from modules.ai_video_studio.ai_video_generator.video_to_video.video_converter import VideoConverter

            return VideoConverter().convert(job)
        raise ValueError(f"Unsupported mode '{mode}'")


_task_dispatcher: TaskDispatcher | None = None


def get_task_dispatcher() -> TaskDispatcher:
    global _task_dispatcher
    if _task_dispatcher is None:
        _task_dispatcher = TaskDispatcher()
    return _task_dispatcher
