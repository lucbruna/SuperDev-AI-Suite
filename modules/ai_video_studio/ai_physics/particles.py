"""Particles — particle system for effects."""
from __future__ import annotations

import random
from typing import Any


class Particles:
    """Simple CPU particle system emitter."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._particles: list[dict[str, Any]] = []

    def emit(self, *, count: int, position: tuple[float, float, float], spread: float = 1.0) -> list[dict[str, Any]]:
        emitted = []
        for _ in range(count):
            particle = {
                "position": [
                    position[0] + self._rng.uniform(-spread, spread),
                    position[1] + self._rng.uniform(-spread, spread),
                    position[2] + self._rng.uniform(-spread, spread),
                ],
                "lifetime": self._rng.uniform(0.5, 2.0),
                "age": 0.0,
            }
            emitted.append(particle)
        self._particles.extend(emitted)
        return emitted

    def update(self, dt: float) -> None:
        for particle in self._particles:
            particle["age"] += dt
        self._particles = [p for p in self._particles if p["age"] < p["lifetime"]]

    def count(self) -> int:
        return len(self._particles)
