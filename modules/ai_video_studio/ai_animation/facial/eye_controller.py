"""Eye controller — eye gaze and pupil movement."""
from __future__ import annotations

import math
from typing import Any


class EyeController:
    """Computes eye gaze offsets and saccade patterns."""

    def gaze_at(self, t: float) -> dict[str, Any]:
        # Slow pan with periodic micro-saccades.
        x = math.sin(t * 0.5) * 0.05 + (0.02 if math.sin(t * 12) > 0.9 else 0.0)
        y = math.cos(t * 0.3) * 0.04
        return {"gaze_x": round(x, 4), "gaze_y": round(y, 4), "saccade": bool(math.sin(t * 12) > 0.9)}
