"""Dolly controller — track-mounted camera movement."""
from __future__ import annotations

from typing import Any


class DollyController:
    """Simulates dolly tracks: dolly-in, dolly-out and trucking."""

    def dolly(self, *, start: tuple[float, float, float], end: tuple[float, float, float], steps: int = 40) -> list[dict[str, Any]]:
        positions = []
        for i in range(steps):
            t = i / max(1, steps - 1)
            eased = t * t * (3 - 2 * t)
            positions.append(
                {
                    "t": round(t, 4),
                    "position": tuple(round(start[k] + (end[k] - start[k]) * eased, 3) for k in range(3)),
                }
            )
        return positions

    def dolly_zoom(self, *, dolly_steps: int = 40, zoom_end: float = 2.0) -> dict[str, Any]:
        return {
            "dolly_positions": dolly_steps,
            "zoom_end": zoom_end,
            "note": "Hitchcock-style dolly zoom",
        }
