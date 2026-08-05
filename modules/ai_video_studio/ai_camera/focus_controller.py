"""Focus controller — autofocus and rack-focus simulation."""
from __future__ import annotations

from typing import Any


class FocusController:
    """Simulates focus pulling and autofocus convergence."""

    def rack_focus(self, *, start_distance: float = 5.0, end_distance: float = 1.0, steps: int = 30) -> list[float]:
        if start_distance <= 0 or end_distance <= 0:
            raise ValueError("distances must be positive")
        return [
            round(start_distance + (end_distance - start_distance) * (i / max(1, steps - 1)), 4)
            for i in range(steps)
        ]

    def autofocus(self, distance: float) -> dict[str, Any]:
        focus = min(10.0, max(0.1, distance))
        confidence = min(1.0, 1.0 / (1.0 + abs(distance - focus)))
        return {"focus_distance": round(focus, 4), "confidence": round(confidence, 3)}

    def bokeh(self, focus_distance: float, depth_of_field: float) -> float:
        if depth_of_field <= 0:
            raise ValueError("depth_of_field must be positive")
        return round(1.0 / (1.0 + depth_of_field * 10.0), 4)
