from __future__ import annotations

import math
from typing import Any


class SpatialReasoning:
    """Spatial reasoning over coordinates and regions."""

    def __init__(self) -> None:
        self._regions: dict[str, list[tuple[float, float]]] = {}

    def add_region(self, name: str, boundary: list[tuple[float, float]]) -> None:
        self._regions[name] = boundary

    async def contains(self, point: tuple[float, float], region: str) -> bool:
        boundary = self._regions.get(region, [])
        if not boundary:
            return False
        x, y = point
        inside = False
        j = len(boundary) - 1
        for i in range(len(boundary)):
            xi, yi = boundary[i]
            xj, yj = boundary[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    async def distance(self, a: tuple[float, float], b: tuple[float, float]) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        point = context.get("point", (0.0, 0.0))
        regions_found = []
        for name in self._regions:
            if await self.contains(point, name):
                regions_found.append(name)
        return {"point": point, "regions": regions_found, "count": len(regions_found)}
