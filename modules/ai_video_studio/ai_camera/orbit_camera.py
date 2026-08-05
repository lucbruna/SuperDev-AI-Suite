"""Orbit camera — orbit a target point at fixed distance."""
from __future__ import annotations

import math
from typing import Any


class OrbitCamera:
    """Computes orbital camera positions around a target."""

    def position(
        self,
        *,
        target: tuple[float, float, float],
        radius: float = 5.0,
        elevation_deg: float = 30.0,
        azimuth_deg: float = 0.0,
    ) -> dict[str, Any]:
        elevation = math.radians(elevation_deg)
        azimuth = math.radians(azimuth_deg)
        x = target[0] + radius * math.cos(elevation) * math.cos(azimuth)
        y = target[1] + radius * math.sin(elevation)
        z = target[2] + radius * math.cos(elevation) * math.sin(azimuth)
        return {"position": (round(x, 3), round(y, 3), round(z, 3)), "target": list(target), "radius": radius}

    def sweep(self, *, target: tuple[float, float, float], radius: float = 5.0, steps: int = 60) -> list[dict[str, Any]]:
        return [
            self.position(target=target, radius=radius, azimuth_deg=360 * i / max(1, steps - 1))
            for i in range(steps)
        ]
