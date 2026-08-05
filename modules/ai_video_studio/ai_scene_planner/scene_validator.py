"""Scene validator — validate scene structure and completeness."""
from __future__ import annotations

from typing import Any

REQUIRED_FIELDS = ("name", "scene_type", "duration")


class SceneValidator:
    """Validates a list of scenes and returns structured issues."""

    def validate(self, scenes: list[dict[str, Any]]) -> dict[str, Any]:
        issues: list[str] = []
        if not scenes:
            return {"valid": False, "issues": ["No scenes provided"], "scene_count": 0}

        for i, scene in enumerate(scenes):
            for field in REQUIRED_FIELDS:
                if field not in scene:
                    issues.append(f"Scene {i}: missing '{field}'")
            duration = scene.get("duration")
            if duration is not None and (not isinstance(duration, (int, float)) or duration <= 0):
                issues.append(f"Scene {i}: duration must be positive")

        return {
            "valid": not issues,
            "issues": issues,
            "scene_count": len(scenes),
            "total_duration": round(sum(s.get("duration", 0) for s in scenes), 3),
        }

    def assert_valid(self, scenes: list[dict[str, Any]]) -> None:
        result = self.validate(scenes)
        if not result["valid"]:
            from modules.ai_video_studio.core.exceptions import ValidationError

            raise ValidationError("; ".join(result["issues"]), field="scenes")


_scene_validator: SceneValidator | None = None


def get_scene_validator() -> SceneValidator:
    global _scene_validator
    if _scene_validator is None:
        _scene_validator = SceneValidator()
    return _scene_validator
