"""Scene duration — computes and normalizes per-scene durations."""
from __future__ import annotations

from typing import Any


class SceneDuration:
    """Assigns durations to boards based on scene type."""

    DEFAULT = 2.5
    TYPE_DURATIONS = {
        "intro": 2.5,
        "opening": 3.0,
        "presentation": 3.0,
        "explanation": 4.0,
        "comparison": 3.5,
        "product": 3.5,
        "testimonial": 3.0,
        "closing": 2.5,
        "credits": 5.0,
        "outro": 3.0,
    }

    def assign(self, board: dict[str, Any]) -> dict[str, Any]:
        board["duration"] = self.TYPE_DURATIONS.get(board.get("type", "presentation"), self.DEFAULT)
        return board

    def normalize(self, boards: list[dict[str, Any]], target: float) -> list[dict[str, Any]]:
        total = sum(b.get("duration", self.DEFAULT) for b in boards)
        if total <= 0:
            return boards
        scale = target / total
        for board in boards:
            board["duration"] = round(board.get("duration", self.DEFAULT) * scale, 3)
        return boards


_scene_duration: SceneDuration | None = None


def get_scene_duration() -> SceneDuration:
    global _scene_duration
    if _scene_duration is None:
        _scene_duration = SceneDuration()
    return _scene_duration
