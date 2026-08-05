"""Camera paths — precomputed camera trajectories."""
from __future__ import annotations

import math


class CameraPaths:
    """Generates parametric camera paths: line, circle, arc, bezier."""

    def line(self, a: tuple[float, float, float], b: tuple[float, float, float], steps: int = 60) -> list[tuple[float, float, float]]:
        return [
            (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)
            for t in (i / max(1, steps - 1) for i in range(steps))
        ]

    def circle(self, center: tuple[float, float, float], radius: float = 5.0, steps: int = 60) -> list[tuple[float, float, float]]:
        return [
            (center[0] + radius * math.cos(2 * math.pi * i / steps), center[1], center[2] + radius * math.sin(2 * math.pi * i / steps))
            for i in range(steps)
        ]

    def arc(self, center: tuple[float, float, float], radius: float, start_deg: float, end_deg: float, steps: int = 30) -> list[tuple[float, float, float]]:
        points = []
        for i in range(steps):
            angle = math.radians(start_deg + (end_deg - start_deg) * i / max(1, steps - 1))
            points.append((center[0] + radius * math.cos(angle), center[1], center[2] + radius * math.sin(angle)))
        return points
