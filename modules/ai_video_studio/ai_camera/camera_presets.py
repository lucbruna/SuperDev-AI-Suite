"""Camera presets — reusable camera configurations."""
from __future__ import annotations

from typing import Any

_PRESETS: dict[str, dict[str, Any]] = {
    "wide": {"focal_length": 24, "sensor_width": 36, "position": (0, 1.6, 8.0)},
    "standard": {"focal_length": 50, "sensor_width": 36, "position": (0, 1.6, 5.0)},
    "portrait": {"focal_length": 85, "sensor_width": 36, "position": (0, 1.6, 2.5)},
    "macro": {"focal_length": 100, "sensor_width": 36, "position": (0, 1.6, 0.8)},
    "telephoto": {"focal_length": 200, "sensor_width": 36, "position": (0, 1.6, 12.0)},
}


class CameraPresets:
    """Provides named camera lens/position presets."""

    def get(self, name: str) -> dict[str, Any]:
        if name not in _PRESETS:
            raise ValueError(f"Unknown preset '{name}'")
        return dict(_PRESETS[name])

    def names(self) -> list[str]:
        return list(_PRESETS.keys())

    def register(self, name: str, config: dict[str, Any]) -> None:
        _PRESETS[name] = config
