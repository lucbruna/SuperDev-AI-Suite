"""Video segmentation — pixel-level masks for video objects."""
from __future__ import annotations

from typing import Any


class VideoSegmentation:
    """Produces per-frame segmentation masks (semantic / instance)."""

    def segment(self, frames: list[dict[str, Any]], *, classes: list[str] | None = None) -> dict[str, Any]:
        classes = classes or ["person", "vehicle", "object"]
        return {
            "frames": len(frames),
            "classes": list(classes),
            "mask_format": "rgba",
            "masks": [{"frame": f["index"], "regions": []} for f in frames],
        }
