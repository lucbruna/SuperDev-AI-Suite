"""Environment physics — combined environment force effects."""
from __future__ import annotations

from typing import Any


class EnvironmentPhysics:
    """Combines gravity, wind, weather and buoyancy into one force field."""

    def __init__(self) -> None:
        self.gravity = 9.81
        self.wind = 0.0
        self.weather = "clear"

    def configure(self, *, gravity: float | None = None, wind: float | None = None, weather: str | None = None) -> None:
        if gravity is not None:
            self.gravity = gravity
        if wind is not None:
            self.wind = wind
        if weather is not None:
            self.weather = weather

    def force_on(self, mass: float) -> dict[str, Any]:
        return {
            "gravity_force": mass * self.gravity,
            "wind_force": mass * self.wind * 0.1,
            "net": [round(mass * self.wind * 0.1, 3), round(-mass * self.gravity, 3), 0.0],
        }
