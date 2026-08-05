"""Sky library — skybox and lighting environment assets."""
from __future__ import annotations

from typing import Any


class SkyLibrary:
    """Catalogues sky environments with lighting conditions."""

    def __init__(self) -> None:
        self._skies: dict[str, dict[str, Any]] = {}

    def register(self, name: str, *, ref: str, time_of_day: str = "day", sun_intensity: float = 1.0) -> None:
        if sun_intensity < 0:
            raise ValueError("sun_intensity must be non-negative")
        self._skies[name] = {"name": name, "ref": ref, "time_of_day": time_of_day, "sun_intensity": sun_intensity}

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._skies[name]) if name in self._skies else None

    def names(self) -> list[str]:
        return list(self._skies.keys())
