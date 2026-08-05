"""Soft body — deformable body model with rest-shape springback."""
from __future__ import annotations

class SoftBody:
    """A soft/deformable body that springs back to its rest shape."""

    def __init__(self, *, nodes: int = 8, stiffness: float = 0.3) -> None:
        if nodes < 3:
            raise ValueError("nodes must be >= 3")
        self.nodes = nodes
        self.stiffness = stiffness
        self._rest: list[list[float]] = [[i, 0.0] for i in range(nodes)]
        self._current: list[list[float]] = [[float(i), 0.0] for i in range(nodes)]

    def deform(self, x: int, amount: float) -> None:
        if 0 <= x < self.nodes:
            self._current[x][1] += amount

    def step(self) -> list[list[float]]:
        for i in range(self.nodes):
            self._current[i][1] += (self._rest[i][1] - self._current[i][1]) * self.stiffness
            self._current[i][0] += (self._rest[i][0] - self._current[i][0]) * self.stiffness * 0.5
        return [[round(c[0], 3), round(c[1], 3)] for c in self._current]
