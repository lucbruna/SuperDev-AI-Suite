"""Fire simulation — flame flicker and spread model."""
from __future__ import annotations

import math
from typing import Any


class FireSimulation:
    """Simulates flame intensity with flicker."""

    def __init__(self, seed: int | None = None) -> None:
        self._flames: list[dict[str, Any]] = []

    def ignite(self, *, count: int = 5, origin: tuple[float, float, float] = (0, 0, 0)) -> list[dict[str, Any]]:
        self._flames = [
            {
                "position": [origin[0] + i * 0.1 - 0.2, origin[1], origin[2]],
                "intensity": 1.0,
                "heat": 0.8,
            }
            for i in range(count)
        ]
        return [dict(f) for f in self._flames]

    def step(self, t: float, dt: float = 1 / 60) -> list[dict[str, Any]]:
        for flame in self._flames:
            flicker = 0.7 + 0.3 * math.sin(t * 13.0 + flame["position"][0] * 7.0)
            flame["intensity"] = round(max(0.0, min(1.0, flicker)), 4)
            flame["heat"] = round(max(0.0, flame["heat"] - dt * 0.1), 4)
        return [dict(f) for f in self._flames]
