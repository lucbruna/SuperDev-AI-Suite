"""Video engine — top-level orchestrator for AI video generation.

The VideoEngine is the single entry point for the whole generator pillar.
It routes a generation request through scheduling, model selection, pipeline
building and rendering, returning a structured result with timing and
quality information.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class VideoEngine:
    """Orchestrates end-to-end video generation requests."""

    def __init__(self) -> None:
        self._requests: dict[str, dict[str, Any]] = {}

    def generate(
        self,
        prompt: str,
        *,
        mode: str = "text_to_video",
        model: str | None = None,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate a video from a prompt or source asset.

        Supported modes: ``text_to_video``, ``image_to_video``,
        ``video_to_video``.
        """
        if not prompt or not prompt.strip():
            raise ValidationError("A non-empty prompt is required", field="prompt")
        if mode not in {"text_to_video", "image_to_video", "video_to_video"}:
            raise ValidationError(f"Unsupported mode '{mode}'", field="mode")

        rid = request_id or f"gen_{len(self._requests) + 1}"
        params = params or {}

        # Deferred imports keep the engine light at import time.
        from modules.ai_video_studio.ai_video_generator.generation_manager import get_generation_manager

        manager = get_generation_manager()
        result = manager.submit(
            prompt=prompt,
            mode=mode,
            model=model,
            params=params,
            request_id=rid,
        )
        self._requests[rid] = {"mode": mode, "result": result}
        return result

    def status(self, request_id: str) -> dict[str, Any] | None:
        """Return the latest status for a previously submitted request."""
        record = self._requests.get(request_id)
        if record is None:
            return None
        return {"request_id": request_id, **record["result"]}

    def list_requests(self) -> list[str]:
        return list(self._requests.keys())

    def clear(self) -> None:
        self._requests.clear()


_video_engine: VideoEngine | None = None


def get_video_engine() -> VideoEngine:
    """Cached singleton video engine."""
    global _video_engine
    if _video_engine is None:
        _video_engine = VideoEngine()
    return _video_engine
