"""Render controller — drive the actual rendering of generated frames."""
from __future__ import annotations

import time
from typing import Any

from modules.ai_video_studio.core.exceptions import RenderingError


class RenderController:
    """Coordinates frame-level rendering and reports progress."""

    def __init__(self) -> None:
        self._renderers: dict[str, Any] = {}
        self._progress: dict[str, dict[str, Any]] = {}

    def register(self, backend: str, renderer: Any) -> None:
        self._renderers[backend] = renderer

    def render(self, job: dict[str, Any], *, backend: str = "local") -> dict[str, Any]:
        renderer = self._renderers.get(backend)
        if renderer is None:
            raise RenderingError(f"No renderer registered for backend '{backend}'")
        frames = job.get("params", {}).get("total_frames", 120)
        started = time.time()
        for frame_index in range(frames):
            renderer.render_frame(job, frame_index)
            if frame_index % max(1, frames // 10) == 0:
                self._progress[job["id"]] = {
                    "frame": frame_index + 1,
                    "total": frames,
                    "percent": round((frame_index + 1) / frames * 100, 1),
                }
        elapsed = time.time() - started
        return {"frames": frames, "elapsed_seconds": round(elapsed, 2), "backend": backend}

    def progress(self, job_id: str) -> dict[str, Any] | None:
        return self._progress.get(job_id)


_render_controller: RenderController | None = None


def get_render_controller() -> RenderController:
    global _render_controller
    if _render_controller is None:
        _render_controller = RenderController()
    return _render_controller
