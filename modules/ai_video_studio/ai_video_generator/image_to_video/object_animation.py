"""Object animation — animate objects detected in a scene."""
from __future__ import annotations

from typing import Any


class ObjectAnimation:
    """Applies per-object motion paths within an animated scene."""

    def __init__(self) -> None:
        self._paths: dict[str, dict[str, Any]] = {}

    def define_path(self, object_name: str, *, waypoints: list[tuple[float, float]]) -> None:
        self._paths[object_name] = {"waypoints": waypoints}

    def position_at(self, object_name: str, t: float) -> tuple[float, float] | None:
        path = self._paths.get(object_name)
        if not path or not path["waypoints"]:
            return None
        waypoints = path["waypoints"]
        if len(waypoints) == 1:
            return waypoints[0]
        scaled = t * (len(waypoints) - 1)
        idx = min(int(scaled), len(waypoints) - 2)
        local = scaled - idx
        a, b = waypoints[idx], waypoints[idx + 1]
        return (a[0] + (b[0] - a[0]) * local, a[1] + (b[1] - a[1]) * local)

    def known_objects(self) -> list[str]:
        return list(self._paths.keys())
