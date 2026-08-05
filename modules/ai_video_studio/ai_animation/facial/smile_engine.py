"""Smile engine — procedural smile dynamics."""
from __future__ import annotations

import math


class SmileEngine:
    """Eases a smile in/out over time for natural expression."""

    def curve(self, t: float, *, intensity: float = 1.0) -> float:
        if not 0 <= t <= 1:
            raise ValueError("t must be in [0, 1]")
        eased = math.sin(t * math.pi)  # smooth bell curve
        return round(max(0.0, min(1.0, eased * intensity)), 4)

    def sample(self, total_frames: int, *, intensity: float = 1.0) -> list[float]:
        return [self.curve(i / max(1, total_frames - 1), intensity=intensity) for i in range(total_frames)]
