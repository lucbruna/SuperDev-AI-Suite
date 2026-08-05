"""Scene animation — animate whole-scene elements (weather, ambience)."""
from __future__ import annotations

from typing import Any


class SceneAnimation:
    """Adds ambient scene animation: wind, rain, light flicker, etc."""

    _EFFECTS = ("wind", "rain", "snow", "flicker", "fog", "none")

    def apply(self, effect: str, frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if effect not in self._EFFECTS:
            effect = "none"
        result = []
        for frame in frames:
            copy = dict(frame)
            if effect == "wind":
                copy["wind"] = {"intensity": 0.3 + 0.2 * (frame["index"] % 3)}
            elif effect == "rain":
                copy["rain"] = {"drops": 40 + (frame["index"] % 20)}
            elif effect == "snow":
                copy["snow"] = {"flakes": 20 + (frame["index"] % 10)}
            elif effect == "flicker":
                copy["flicker"] = {"level": 0.9 if frame["index"] % 4 else 0.6}
            elif effect == "fog":
                copy["fog"] = {"density": 0.2 + 0.1 * (frame["index"] % 5)}
            result.append(copy)
        return result

    def available_effects(self) -> list[str]:
        return list(self._EFFECTS)
