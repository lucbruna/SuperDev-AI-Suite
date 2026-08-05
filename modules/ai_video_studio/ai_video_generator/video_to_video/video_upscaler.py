"""Video upscaler — increase resolution of a video."""
from __future__ import annotations

from typing import Any

_TARGETS = {
    "480p": (854, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}


class VideoUpscaler:
    """Upscales a video to a target resolution with a chosen model."""

    def upscale(self, source: str, *, target: str = "1080p", model: str = "esrgan") -> dict[str, Any]:
        if target not in _TARGETS:
            raise ValueError(f"Unknown target resolution '{target}'")
        width, height = _TARGETS[target]
        return {
            "source": source,
            "target": target,
            "width": width,
            "height": height,
            "model": model,
        }

    def targets(self) -> dict[str, tuple[int, int]]:
        return dict(_TARGETS)
