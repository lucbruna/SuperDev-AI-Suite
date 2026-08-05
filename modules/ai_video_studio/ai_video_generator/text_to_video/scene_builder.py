"""Scene builder — assemble a scene blueprint from a parsed prompt."""
from __future__ import annotations

from typing import Any


class SceneBuilder:
    """Combines parsed cues into a structured scene plan."""

    def build(self, parsed: dict[str, Any]) -> dict[str, Any]:
        return {
            "description": parsed["subject"],
            "style": parsed["style"],
            "camera": parsed["camera"],
            "lighting": parsed["lighting"],
            "shots": [{"index": 0, "description": parsed["subject"], "duration": 5.0}],
            "quality_estimate": 0.8,
        }

    def add_shot(self, scene: dict[str, Any], description: str, duration: float = 3.0) -> dict[str, Any]:
        shot = {"index": len(scene["shots"]), "description": description, "duration": duration}
        scene["shots"].append(shot)
        return shot
