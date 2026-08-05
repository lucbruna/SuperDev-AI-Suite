"""Wind engine — wind force fields for environment physics."""
from __future__ import annotations

import math
from typing import Any


class WindEngine:
    """Generates wind vectors with gusts and turbulence."""

    def force(self, t: float, *, base_speed: float = 3.0, gust: float = 1.5, direction: tuple[float, float, float] = (1, 0, 0)) -> dict[str, Any]:
        gust_phase = math.sin(t * 0.7) * gust
        turbulence = math.sin(t * 5.0) * 0.3
        speed = max(0.0, base_speed + gust_phase + turbulence)
        magnitude = math.sqrt(sum(d * d for d in direction))
        unit = tuple(d / magnitude for d in direction) if magnitude else direction
        return {
            "speed": round(speed, 3),
            "direction": list(unit),
            "vector": [round(unit[i] * speed, 3) for i in range(3)],
        }
