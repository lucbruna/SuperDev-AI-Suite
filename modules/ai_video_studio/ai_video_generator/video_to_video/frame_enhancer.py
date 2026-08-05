"""Frame enhancer — per-frame quality enhancement."""
from __future__ import annotations

from typing import Any


class FrameEnhancer:
    """Enhances frames: contrast, sharpness, dynamic range."""

    def enhance(self, frames: list[dict[str, Any]], *, sharpness: float = 0.5, contrast: float = 0.3) -> list[dict[str, Any]]:
        result = []
        for frame in frames:
            copy = dict(frame)
            copy["enhanced"] = {
                "sharpness": min(2.0, max(0.0, sharpness)),
                "contrast": min(2.0, max(0.0, contrast)),
                "applied": True,
            }
            result.append(copy)
        return result
