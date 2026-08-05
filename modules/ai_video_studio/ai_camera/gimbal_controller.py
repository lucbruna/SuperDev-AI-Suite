"""Gimbal controller — stabilised 3-axis camera mounting."""
from __future__ import annotations

import math
from typing import Any


class GimbalController:
    """Simulates gimbal-stabilised orientation with smoothing."""

    def stabilize(self, raw_pan: float, raw_tilt: float, *, smoothing: float = 0.8) -> dict[str, Any]:
        if not 0 <= smoothing <= 1:
            raise ValueError("smoothing must be in [0, 1]")
        return {
            "pan": round(raw_pan * smoothing, 4),
            "tilt": round(raw_tilt * smoothing, 4),
            "roll_compensation": round(math.sin(raw_pan) * 0.01 * smoothing, 4),
        }
