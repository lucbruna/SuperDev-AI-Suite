"""Cloth simulation — mass-spring cloth model."""
from __future__ import annotations

from typing import Any


class ClothSimulation:
    """Simulates cloth as a grid of masses connected by springs."""

    def __init__(self, *, rows: int = 10, cols: int = 10, stiffness: float = 0.5) -> None:
        self.rows = rows
        self.cols = cols
        self.stiffness = stiffness
        self._masses: list[dict[str, Any]] = []

    def init_cloth(self) -> None:
        self._masses = [
            {"row": r, "col": c, "x": c, "y": 0.0, "z": r, "pinned": r == 0}
            for r in range(self.rows)
            for c in range(self.cols)
        ]

    def step(self, wind: float = 0.0) -> list[dict[str, Any]]:
        if not self._masses:
            self.init_cloth()
        for mass in self._masses:
            if mass["pinned"]:
                continue
            force = wind * self.stiffness
            mass["y"] += force * 0.02
        return [dict(m) for m in self._masses]
