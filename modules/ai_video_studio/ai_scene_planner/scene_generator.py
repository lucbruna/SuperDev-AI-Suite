"""Scene generator — generate scenes from a video brief."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

SCENE_TYPES = ("intro", "content", "transition", "outro", "title_card", "b_roll", "highlight", "credits")


class SceneGenerator:
    """Deterministic scene generation from a brief."""

    def generate(self, brief: str, num_scenes: int = 3, duration: float = 10.0) -> list[dict[str, Any]]:
        if num_scenes < 1:
            raise ValidationError("num_scenes must be >= 1", field="num_scenes")
        if duration <= 0:
            raise ValidationError("duration must be positive", field="duration")

        words = (brief or "").split() or ["Scene"]
        per_scene = duration / num_scenes
        words_per_scene = max(1, len(words) // num_scenes)
        scenes: list[dict[str, Any]] = []

        for i in range(num_scenes):
            start = i * words_per_scene
            chunk = words[start : min(start + words_per_scene, len(words))]
            text = " ".join(chunk) if chunk else f"Scene {i + 1}"
            first = i == 0
            last = i == num_scenes - 1
            scenes.append(
                {
                    "index": i,
                    "name": f"Scene {i + 1}",
                    "description": text,
                    "scene_type": "intro" if first else ("outro" if last and num_scenes > 2 else "content"),
                    "duration": round(per_scene, 3),
                    "transition_in": "none" if first else "fade",
                    "transition_out": "fade",
                }
            )
        return scenes


_scene_generator: SceneGenerator | None = None


def get_scene_generator() -> SceneGenerator:
    global _scene_generator
    if _scene_generator is None:
        _scene_generator = SceneGenerator()
    return _scene_generator
