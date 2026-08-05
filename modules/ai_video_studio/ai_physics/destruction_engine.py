"""Destruction engine — object breakage and fragmentation."""
from __future__ import annotations

import math
from typing import Any


class DestructionEngine:
    """Shatters bodies into fragments based on impact energy."""

    def shatter(self, *, object_name: str, energy: float, fragments: int = 8) -> dict[str, Any]:
        if energy < 0:
            raise ValueError("energy must be non-negative")
        threshold = 5.0
        if energy < threshold:
            return {"object": object_name, "destroyed": False, "fragments": 0}
        count = max(2, min(fragments, int(energy / threshold)))
        return {
            "object": object_name,
            "destroyed": True,
            "fragments": count,
            "fragment_mass": round(1.0 / count, 3),
            "energy": round(energy, 2),
        }

    def debris_trajectory(self, fragment_index: int, total: int, energy: float) -> list[dict[str, Any]]:
        angle = (math.pi * 2 * fragment_index / total) + math.pi / total
        return [
            {"t": round(t / 10, 1), "x": round(math.cos(angle) * energy * 0.1 * t, 3), "y": round(energy * 0.02 * t, 3)}
            for t in range(11)
        ]
