"""Gravity — gravity field configurations and forces."""
from __future__ import annotations

from typing import Any

_DEFAULT_GRAVITY = 9.81


class Gravity:
    """Applies gravity vectors to bodies."""

    def force(self, mass: float, *, gravity: float | None = None) -> dict[str, Any]:
        g = gravity if gravity is not None else _DEFAULT_GRAVITY
        return {"force": mass * g, "direction": [0, -1, 0], "magnitude": round(g, 4)}

    def planet_gravity(self, planet: str) -> float:
        values = {
            "earth": 9.81,
            "moon": 1.62,
            "mars": 3.71,
            "jupiter": 24.79,
            "space": 0.0,
        }
        return values.get(planet, _DEFAULT_GRAVITY)
