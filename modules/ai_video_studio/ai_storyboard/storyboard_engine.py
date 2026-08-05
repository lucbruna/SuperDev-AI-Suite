"""Storyboard engine — coordinates scene, layout, timeline and preview builders."""
from __future__ import annotations

from typing import Any


class StoryboardEngine:
    """Assembles a full storyboard from a scene plan."""

    def __init__(self) -> None:
        from modules.ai_video_studio.ai_storyboard.storyboard_optimizer import get_storyboard_optimizer
        from modules.ai_video_studio.ai_storyboard.scenes.intro_scene import get_intro_scene
        from modules.ai_video_studio.ai_storyboard.scenes.opening_scene import get_opening_scene
        from modules.ai_video_studio.ai_storyboard.scenes.presentation_scene import get_presentation_scene
        from modules.ai_video_studio.ai_storyboard.scenes.explanation_scene import get_explanation_scene
        from modules.ai_video_studio.ai_storyboard.scenes.comparison_scene import get_comparison_scene
        from modules.ai_video_studio.ai_storyboard.scenes.product_scene import get_product_scene
        from modules.ai_video_studio.ai_storyboard.scenes.testimonial_scene import get_testimonial_scene
        from modules.ai_video_studio.ai_storyboard.scenes.closing_scene import get_closing_scene
        from modules.ai_video_studio.ai_storyboard.scenes.credits_scene import get_credits_scene
        from modules.ai_video_studio.ai_storyboard.scenes.outro_scene import get_outro_scene
        from modules.ai_video_studio.ai_storyboard.layouts.cinematic_layout import get_cinematic_layout
        from modules.ai_video_studio.ai_storyboard.timeline.storyboard_timeline import get_storyboard_timeline

        self.optimizer = get_storyboard_optimizer()
        self._scenes = {
            "intro": get_intro_scene,
            "opening": get_opening_scene,
            "presentation": get_presentation_scene,
            "explanation": get_explanation_scene,
            "comparison": get_comparison_scene,
            "product": get_product_scene,
            "testimonial": get_testimonial_scene,
            "closing": get_closing_scene,
            "credits": get_credits_scene,
            "outro": get_outro_scene,
        }
        self._layouts = {"cinematic": get_cinematic_layout}
        self._timeline = get_storyboard_timeline

    def build(self, plan: dict[str, Any], layout: str = "cinematic") -> dict[str, Any]:
        """Build a storyboard from a scene plan dict."""
        scenes = plan.get("scenes", [])
        boards = []
        for scene in scenes:
            scene_type = scene.get("type", "presentation")
            builder = self._scenes.get(scene_type, self._scenes["presentation"])
            board = builder().render(scene)
            boards.append(board)
        layout_builder = self._layouts.get(layout, self._layouts["cinematic"])
        layout_spec = layout_builder().spec()
        timeline = self._timeline().build(boards)
        optimized = self.optimizer.optimize(boards, layout_spec)
        return {"boards": optimized, "layout": layout_spec, "timeline": timeline, "total_frames": len(optimized)}


_storyboard_engine: StoryboardEngine | None = None


def get_storyboard_engine() -> StoryboardEngine:
    global _storyboard_engine
    if _storyboard_engine is None:
        _storyboard_engine = StoryboardEngine()
    return _storyboard_engine
