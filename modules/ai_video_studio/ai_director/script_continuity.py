"""Script continuity — verifies consistency across scenes."""
from __future__ import annotations

from typing import Any


class ScriptContinuity:
    """Checks continuity signals across a set of scenes."""

    def check(self, scenes: list[dict[str, Any]]) -> dict[str, Any]:
        if not scenes:
            return {"consistent": True, "issues": []}
        locations = {scene.get("location") for scene in scenes if scene.get("location")}
        characters = {character for scene in scenes for character in scene.get("characters", [])}
        issues: list[str] = []
        if len(locations) > 1 and len(scenes) > 3:
            issues.append("Multiple locations detected — verify transitions.")
        return {
            "consistent": not issues,
            "issues": issues,
            "locations": len(locations),
            "characters": len(characters),
        }


_script_continuity: ScriptContinuity | None = None


def get_script_continuity() -> ScriptContinuity:
    global _script_continuity
    if _script_continuity is None:
        _script_continuity = ScriptContinuity()
    return _script_continuity
