"""Lighting director — define light rigs for a scene."""
from __future__ import annotations

from typing import Any

_LIGHT_RIGS: dict[str, dict[str, Any]] = {
    "golden hour": {"key": "warm_sun", "intensity": 0.9, "color_temp": 3500, "fill": 0.3},
    "neon": {"key": "neon_panel", "intensity": 0.8, "color_temp": 6000, "fill": 0.4},
    "studio": {"key": "softbox", "intensity": 1.0, "color_temp": 5500, "fill": 0.6},
    "soft": {"key": "diffused", "intensity": 0.7, "color_temp": 5000, "fill": 0.5},
    "dramatic": {"key": "hard_spot", "intensity": 1.0, "color_temp": 4500, "fill": 0.1},
    "backlit": {"key": "rim", "intensity": 0.8, "color_temp": 6500, "fill": 0.2},
    "moody": {"key": "practical", "intensity": 0.5, "color_temp": 3000, "fill": 0.2},
}


class LightingDirector:
    """Builds a lighting rig matching the requested mood."""

    def rig(self, lighting: str) -> dict[str, Any]:
        base = _LIGHT_RIGS.get(lighting, _LIGHT_RIGS["natural"])
        return dict(base)

    def add_light(self, rig: dict[str, Any], name: str, spec: dict[str, Any]) -> None:
        rig.setdefault("extra_lights", {})[name] = spec

    def available_rigs(self) -> list[str]:
        return list(_LIGHT_RIGS.keys())
