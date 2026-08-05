"""Handheld camera — realistic handheld shake simulation."""
from __future__ import annotations

import math
from typing import Any


class HandheldCamera:
    """Adds organic micro-shake to camera positions."""

    def shake(self, t: float, *, intensity: float = 0.02) -> dict[str, Any]:
        if intensity < 0:
            raise ValueError("intensity must be non-negative")
        noise_x = math.sin(t * 47.0) * 0.5 + math.sin(t * 91.0) * 0.3 + math.sin(t * 7.0) * 0.2
        noise_y = math.cos(t * 53.0) * 0.5 + math.cos(t * 83.0) * 0.3 + math.cos(t * 11.0) * 0.2
        return {
            "dx": round(noise_x * intensity, 4),
            "dy": round(noise_y * intensity, 4),
            "roll": round(math.sin(t * 29.0) * intensity * 0.5, 4),
        }
