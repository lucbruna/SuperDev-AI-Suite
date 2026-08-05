"""Smoke simulation — billowing smoke plume model."""
from __future__ import annotations

from typing import Any


class SmokeSimulation:
    """Simulates smoke puffs with rise and dissipation."""

    def __init__(self, seed: int | None = None) -> None:
        import random

        self._rng = random.Random(seed)
        self._puffs: list[dict[str, Any]] = []

    def emit(self, *, count: int = 5, origin: tuple[float, float, float] = (0, 0, 0)) -> list[dict[str, Any]]:
        emitted = []
        for _ in range(count):
            puff = {
                "position": [origin[0] + self._rng.uniform(-0.2, 0.2), origin[1], origin[2] + self._rng.uniform(-0.2, 0.2)],
                "density": self._rng.uniform(0.6, 1.0),
                "radius": self._rng.uniform(0.2, 0.5),
            }
            emitted.append(puff)
        self._puffs.extend(emitted)
        return emitted

    def step(self, dt: float = 1 / 60) -> list[dict[str, Any]]:
        for puff in self._puffs:
            puff["position"][1] += dt * 0.5  # rise
            puff["radius"] += dt * 0.1  # expand
            puff["density"] = max(0.0, puff["density"] - dt * 0.2)  # dissipate
        self._puffs = [p for p in self._puffs if p["density"] > 0.02]
        return [dict(p) for p in self._puffs]
