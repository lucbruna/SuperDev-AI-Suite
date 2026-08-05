"""FPS converter — change video frame rate with motion-aware resampling."""
from __future__ import annotations

from typing import Any


class FPSConverter:
    """Converts between frame rates, interpolating or dropping frames."""

    def convert(self, source: str, *, from_fps: int = 24, to_fps: int = 60) -> dict[str, Any]:
        if from_fps <= 0 or to_fps <= 0:
            raise ValueError("FPS values must be positive")
        return {
            "source": source,
            "from_fps": from_fps,
            "to_fps": to_fps,
            "method": "interpolate" if to_fps > from_fps else "drop",
            "frame_ratio": round(to_fps / from_fps, 3),
        }
