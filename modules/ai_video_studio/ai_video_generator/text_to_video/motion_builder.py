"""Motion builder — plan object and camera motion for a shot."""
from __future__ import annotations

from typing import Any


class MotionBuilder:
    """Builds motion curves (linear, ease, oscillate) for scene elements."""

    def build(self, shot: dict[str, Any], duration: float = 5.0) -> dict[str, Any]:
        return {
            "shot": shot.get("index", 0),
            "objects": [],
            "camera": {"type": "pan", "amplitude": 0.1, "period": duration},
        }

    def add_object_motion(
        self,
        motion: dict[str, Any],
        *,
        object_name: str,
        curve: str = "linear",
        start: tuple[float, float, float] = (0, 0, 0),
        end: tuple[float, float, float] = (1, 0, 0),
    ) -> None:
        motion["objects"].append(
            {"object": object_name, "curve": curve, "start": start, "end": end}
        )

    def sample(self, motion: dict[str, Any], t: float) -> list[dict[str, Any]]:
        samples = []
        for obj in motion["objects"]:
            curve = obj["curve"]
            if curve == "ease":
                factor = t * t * (3 - 2 * t)
            elif curve == "oscillate":
                import math

                factor = (math.sin(t * math.pi * 2) + 1) / 2
            else:
                factor = t
            position = tuple(
                obj["start"][i] + (obj["end"][i] - obj["start"][i]) * factor for i in range(3)
            )
            samples.append({"object": obj["object"], "position": position})
        return samples
