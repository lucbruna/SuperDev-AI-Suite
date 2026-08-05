"""Shot generator — generate shots for a scene."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

SHOT_TYPES = ("wide", "medium", "close_up", "extreme_close_up", "over_shoulder", "aerial", "establishing")


class ShotGenerator:
    """Deterministic shot list generation for a scene."""

    def generate(self, scene: dict[str, Any], num_shots: int = 3) -> list[dict[str, Any]]:
        if num_shots < 1:
            raise ValidationError("num_shots must be >= 1", field="num_shots")
        scene_duration = scene.get("duration", 5.0)
        per_shot = scene_duration / num_shots
        shots: list[dict[str, Any]] = []
        for i in range(num_shots):
            shots.append(
                {
                    "index": i,
                    "type": SHOT_TYPES[i % len(SHOT_TYPES)],
                    "duration": round(per_shot, 3),
                    "camera": "static",
                    "subject": scene.get("description") or scene.get("name") or "main subject",
                    "action": "hold",
                }
            )
        return shots

    def suggest_camera_movement(self, shot_type: str) -> str:
        movements = {
            "wide": "slow push in",
            "medium": "subtle pan",
            "close_up": "slight tilt down",
            "extreme_close_up": "static",
            "over_shoulder": "tracking",
            "aerial": "orbit",
            "establishing": "slow zoom out",
        }
        return movements.get(shot_type, "static")


_shot_generator: ShotGenerator | None = None


def get_shot_generator() -> ShotGenerator:
    global _shot_generator
    if _shot_generator is None:
        _shot_generator = ShotGenerator()
    return _shot_generator
