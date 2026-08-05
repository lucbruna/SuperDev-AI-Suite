"""Frame generator — produce raw frames from a scene blueprint."""
from __future__ import annotations

from typing import Any


class FrameGenerator:
    """Generates a list of frame descriptors for the pipeline."""

    def generate_frames(self, scene: dict[str, Any], params: dict[str, Any]) -> list[dict[str, Any]]:
        total = max(1, int(params.get("total_frames", 120)))
        width = params.get("width", 1280)
        height = params.get("height", 720)
        frames = [
            {
                "index": i,
                "width": width,
                "height": height,
                "scene": scene.get("description", ""),
                "style": scene.get("style", "cinematic"),
                "seed": hash((scene.get("description", ""), i)) % (2**32),
            }
            for i in range(total)
        ]
        return frames
