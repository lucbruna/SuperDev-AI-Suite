"""Eye tracking — compute gaze direction from target or motion."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp


class EyeTracking:
    """Computes normalized gaze (x, y) toward a target point."""

    def track(self, *, target_x: float = 0.0, target_y: float = 0.0,
              smooth: float = 0.0) -> dict[str, Any]:
        """``target_x/y`` in normalized space (-1..1); ``smooth`` 0..1."""
        x = clamp(target_x, -1.0, 1.0)
        y = clamp(target_y, -1.0, 1.0)
        return {
            "gaze_x": round(x * (1 - smooth * 0.5), 3),
            "gaze_y": round(y * (1 - smooth * 0.5), 3),
            "smooth": clamp(smooth, 0.0, 1.0),
        }


_eye_tracking: EyeTracking | None = None


def get_eye_tracking() -> EyeTracking:
    global _eye_tracking
    if _eye_tracking is None:
        _eye_tracking = EyeTracking()
    return _eye_tracking
