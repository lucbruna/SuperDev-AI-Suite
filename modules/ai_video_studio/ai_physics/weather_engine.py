"""Weather engine — weather systems affecting scene physics."""
from __future__ import annotations

from typing import Any

_CONDITIONS = ("clear", "rain", "snow", "storm", "fog", "windy")


class WeatherEngine:
    """Deterministic weather condition profiles."""

    def condition(self, name: str = "clear") -> dict[str, Any]:
        if name not in _CONDITIONS:
            raise ValueError(f"Unknown condition '{name}'")
        profiles = {
            "clear": {"precipitation": 0.0, "wind": 2.0, "visibility": 1.0},
            "rain": {"precipitation": 0.7, "wind": 4.0, "visibility": 0.6},
            "snow": {"precipitation": 0.5, "wind": 3.0, "visibility": 0.5},
            "storm": {"precipitation": 1.0, "wind": 12.0, "visibility": 0.2},
            "fog": {"precipitation": 0.1, "wind": 1.0, "visibility": 0.15},
            "windy": {"precipitation": 0.0, "wind": 9.0, "visibility": 0.9},
        }
        return {"condition": name, **profiles[name]}

    def transition(self, a: str, b: str, t: float) -> dict[str, Any]:
        if not 0 <= t <= 1:
            raise ValueError("t must be in [0, 1]")
        pa, pb = self.condition(a), self.condition(b)
        return {
            "condition": "transition",
            "precipitation": round(pa["precipitation"] + (pb["precipitation"] - pa["precipitation"]) * t, 3),
            "wind": round(pa["wind"] + (pb["wind"] - pa["wind"]) * t, 3),
            "visibility": round(pa["visibility"] + (pb["visibility"] - pa["visibility"]) * t, 3),
        }

    def available_conditions(self) -> list[str]:
        return list(_CONDITIONS)
