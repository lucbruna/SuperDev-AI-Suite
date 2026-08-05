"""Shot list — enumerates the shots required for each scene."""
from __future__ import annotations

from typing import Any


class ShotList:
    """Builds a per-scene shot list."""

    def build(self, scenes: int = 1, per_scene: int = 3) -> list[dict[str, Any]]:
        shots: list[dict[str, Any]] = []
        for scene in range(1, scenes + 1):
            for index in range(per_scene):
                shots.append({"scene": scene, "shot": index + 1, "status": "pending"})
        return shots


_shot_list: ShotList | None = None


def get_shot_list() -> ShotList:
    global _shot_list
    if _shot_list is None:
        _shot_list = ShotList()
    return _shot_list
