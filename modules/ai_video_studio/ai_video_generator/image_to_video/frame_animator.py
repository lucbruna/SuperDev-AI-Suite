"""Frame animator — create a sequence of frames from an image + depth."""
from __future__ import annotations

from typing import Any


class FrameAnimator:
    """Animates an image by applying per-layer motion over time."""

    def animate(self, image: dict[str, Any], depth: dict[str, Any], params: dict[str, Any]) -> list[dict[str, Any]]:
        total = max(1, int(params.get("total_frames", 96)))
        width = image.get("width") or params.get("width", 1280)
        height = image.get("height") or params.get("height", 720)
        frames = []
        for i in range(total):
            t = i / max(1, total - 1)
            frames.append(
                {
                    "index": i,
                    "t": round(t, 4),
                    "width": width,
                    "height": height,
                    "image_ref": image.get("ref"),
                    "layers": [
                        {"name": layer["name"], "offset_x": round((0.5 - layer["depth"]) * t * 20, 2)}
                        for layer in depth.get("layers", [])
                    ],
                }
            )
        return frames
