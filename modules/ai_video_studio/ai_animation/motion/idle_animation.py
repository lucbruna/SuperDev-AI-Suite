"""Idle animation — subtle breathing and weight-shift idle motion."""
from __future__ import annotations

import math
from typing import Any


class IdleAnimation:
    """Generates micro-movements for standing characters."""

    def pose(self, t: float) -> dict[str, Any]:
        breath = math.sin(t * math.pi * 2 * 0.25) * 0.015
        weight_shift = math.sin(t * math.pi * 2 * 0.1) * 0.02
        return {
            "chest_breath": round(breath, 4),
            "weight_shift": round(weight_shift, 4),
            "head_micro": round(math.sin(t * math.pi * 2 * 0.07) * 0.01, 4),
        }

    def cycle(self, frames: int) -> list[dict[str, Any]]:
        return [self.pose(i / max(1, frames - 1)) for i in range(frames)]
