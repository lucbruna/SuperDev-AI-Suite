"""Fluid simulation — lightweight fluid behaviour model."""
from __future__ import annotations

class FluidSimulation:
    """Simple heightfield fluid model for surface effects."""

    def __init__(self, *, size: int = 16, viscosity: float = 0.1) -> None:
        self.size = size
        self.viscosity = viscosity
        self._heights = [[0.0 for _ in range(size)] for _ in range(size)]

    def add_drop(self, x: int, y: int, amount: float = 1.0) -> None:
        if 0 <= x < self.size and 0 <= y < self.size:
            self._heights[x][y] = min(10.0, self._heights[x][y] + amount)

    def step(self, dt: float = 1 / 60) -> list[list[float]]:
        new = [[0.0 for _ in range(self.size)] for _ in range(self.size)]
        for x in range(self.size):
            for y in range(self.size):
                neighbors = 0.0
                count = 0
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        neighbors += self._heights[nx][ny]
                        count += 1
                avg = neighbors / count if count else 0.0
                new[x][y] = self._heights[x][y] + (avg - self._heights[x][y]) * min(1.0, self.viscosity * dt * 60)
        self._heights = new
        return [list(row) for row in self._heights]
