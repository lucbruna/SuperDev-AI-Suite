"""Zoom controller — zoom lens simulation with ramping."""
from __future__ import annotations

class ZoomController:
    """Simulates optical zoom ramps (in, out, crash, slow)."""

    def ramp(self, *, start: float = 1.0, end: float = 2.0, mode: str = "linear", steps: int = 30) -> list[float]:
        if start <= 0 or end <= 0:
            raise ValueError("zoom values must be positive")
        values: list[float] = []
        for i in range(steps):
            t = i / max(1, steps - 1)
            if mode == "crash":
                eased = t**3
            elif mode == "slow":
                eased = t**0.5
            else:
                eased = t
            values.append(round(start + (end - start) * eased, 4))
        return values
