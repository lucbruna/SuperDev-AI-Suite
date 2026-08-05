"""Cinematic grading — teal-orange and blockbuster presets.

Both presets configure a :class:`GradePipeline` with the classic teal-shadows /
orange-highlights split, a gentle S-curve and slightly crushed blacks.
"""
from __future__ import annotations

from modules.ai_video_studio.ai_color_grading.grading_engine import GradePipeline
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.cinematic")


class CinematicGrading:
    def teal_orange(self, strength: float = 0.5) -> GradePipeline:
        """The Hollywood look: teal shadows, orange highlights."""
        pipeline = GradePipeline()
        pipeline.lift = (-0.02 * strength, 0.02 * strength, 0.02 * strength)
        pipeline.gamma = (0.95, 1.0, 1.02)
        pipeline.gain = (1.05, 1.0, 0.96)
        pipeline.saturation = 1.0 + 0.1 * strength
        pipeline.contrast = 0.12 * strength
        pipeline.temp = -0.2 * strength
        pipeline.tint = 0.1 * strength
        return pipeline

    def blockbuster(self, strength: float = 0.6) -> GradePipeline:
        """Punchy contrast with lifted highlights and deeper blacks."""
        pipeline = GradePipeline()
        pipeline.exposure = 0.1 * strength
        pipeline.lift = (-0.03 * strength, -0.01 * strength, -0.01 * strength)
        pipeline.gamma = (1.0, 0.98, 0.97)
        pipeline.gain = (1.02, 1.04, 1.06)
        pipeline.saturation = 1.2 * strength + 0.4
        pipeline.contrast = 0.2 * strength
        return pipeline

    def presets(self) -> dict[str, str]:
        return {"teal_orange": "Teal & Orange", "blockbuster": "Blockbuster"}
