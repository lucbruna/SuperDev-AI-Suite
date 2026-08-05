"""Scene planner engine — orchestrates the full scene planning pipeline."""
from __future__ import annotations

from typing import Any


class ScenePlannerEngine:
    """High-level scene planning: generate scenes, shots, and enrich them."""

    def __init__(self) -> None:
        from modules.ai_video_studio.ai_scene_planner.scene_generator import get_scene_generator
        from modules.ai_video_studio.ai_scene_planner.shot_generator import get_shot_generator
        from modules.ai_video_studio.ai_scene_planner.location_planner import get_location_planner
        from modules.ai_video_studio.ai_scene_planner.character_planner import get_character_planner
        from modules.ai_video_studio.ai_scene_planner.lighting_planner import get_lighting_planner
        from modules.ai_video_studio.ai_scene_planner.camera_planner import get_camera_planner
        from modules.ai_video_studio.ai_scene_planner.environment_planner import get_environment_planner
        from modules.ai_video_studio.ai_scene_planner.continuity_engine import get_continuity_engine
        from modules.ai_video_studio.ai_scene_planner.scene_validator import get_scene_validator
        from modules.ai_video_studio.ai_scene_planner.scene_optimizer import get_scene_optimizer
        from modules.ai_video_studio.ai_scene_planner.planner_reports import get_planner_reports

        self.scene_generator = get_scene_generator()
        self.shot_generator = get_shot_generator()
        self.location_planner = get_location_planner()
        self.character_planner = get_character_planner()
        self.lighting_planner = get_lighting_planner()
        self.camera_planner = get_camera_planner()
        self.environment_planner = get_environment_planner()
        self.continuity = get_continuity_engine()
        self.validator = get_scene_validator()
        self.optimizer = get_scene_optimizer()
        self.reports = get_planner_reports()

    def plan(self, brief: str, num_scenes: int = 3, duration: float = 10.0, shots_per_scene: int = 2) -> dict[str, Any]:
        """Generate a complete scene plan with shots and enrichment."""
        scenes = self.scene_generator.generate(brief, num_scenes=num_scenes, duration=duration)
        self.optimizer.optimize_durations(scenes, duration)

        location = self.location_planner.plan(brief)
        environment = self.environment_planner.suggest_for_brief(brief)
        lighting = self.lighting_planner.plan(location["mood"])
        characters = self.character_planner.plan(scenes)

        enriched: list[dict[str, Any]] = []
        for i, scene in enumerate(scenes):
            scene["location"] = location["location"]
            scene["environment"] = environment["environment"]
            scene["lighting"] = lighting["scheme"]
            scene["character"] = characters[i]["character"]
            scene["shots"] = self.shot_generator.generate(scene, num_shots=shots_per_scene)
            enriched.append(scene)

        validation = self.validator.validate(enriched)
        continuity = self.continuity.check(enriched)

        return {
            "brief": brief,
            "scenes": enriched,
            "summary": self.reports.summary(enriched),
            "validation": validation,
            "continuity": continuity,
            "location": location,
            "environment": environment,
            "lighting": lighting,
        }


_scene_planner_engine: ScenePlannerEngine | None = None


def get_scene_planner_engine() -> ScenePlannerEngine:
    global _scene_planner_engine
    if _scene_planner_engine is None:
        _scene_planner_engine = ScenePlannerEngine()
    return _scene_planner_engine
