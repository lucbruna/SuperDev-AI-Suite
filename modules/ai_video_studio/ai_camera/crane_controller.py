"""Crane controller — overhead crane camera sweeps."""
from __future__ import annotations

from typing import Any


class CraneController:
    """Simulates crane/jib movements for high-angle shots."""

    def sweep(self, *, base: tuple[float, float, float], height: float = 6.0, arc_deg: float = 90.0, steps: int = 30) -> list[dict[str, Any]]:
        import math

        points = []
        for i in range(steps):
            angle = math.radians(arc_deg * i / max(1, steps - 1))
            points.append(
                {
                    "t": round(i / max(1, steps - 1), 4),
                    "position": (
                        round(base[0] + math.sin(angle) * height * 0.5, 3),
                        round(base[1] + height * (i / max(1, steps - 1)), 3),
                        round(base[2] + math.cos(angle) * height * 0.5, 3),
                    ),
                }
            )
        return points

    def crane_up(self, *, base: tuple[float, float, float], height: float, steps: int = 20) -> list[dict[str, Any]]:
        return [
            {"t": round(i / max(1, steps - 1), 4), "position": (base[0], round(base[1] + height * i / max(1, steps - 1), 3), base[2])}
            for i in range(steps)
        ]
