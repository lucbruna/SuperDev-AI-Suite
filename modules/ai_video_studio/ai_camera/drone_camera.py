"""Drone camera — aerial drone flight behaviours."""
from __future__ import annotations

import math
from typing import Any


class DroneCamera:
    """Simulates drone flights: hover, orbit, reveal, chase."""

    def flight_path(self, mode: str, *, altitude: float = 30.0, radius: float = 40.0, steps: int = 60) -> list[dict[str, Any]]:
        points: list[dict[str, Any]] = []
        for i in range(steps):
            t = i / max(1, steps - 1)
            if mode == "orbit":
                angle = t * math.pi * 2
                position = (radius * math.cos(angle), altitude, radius * math.sin(angle))
            elif mode == "reveal":
                position = (t * radius, altitude, 0.0)
            elif mode == "chase":
                position = (radius * 0.2, altitude * 0.6, t * radius)
            else:  # hover
                position = (0, altitude, radius * 0.3)
            points.append({"t": round(t, 4), "position": position})
        return points
