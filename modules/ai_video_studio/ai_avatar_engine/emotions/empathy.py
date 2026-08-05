"""Empathy emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="empathy",
        facial={"smile": 0.25, "brow_raise": 0.4, "brow_frown": 0.2,
                "mouth_open": 0.1, "eye_open": 0.9, "head_tilt": 6.0},
        body={"lean": 0.3, "arm_energy": 0.3, "posture": 0.4},
        voice={"pitch_shift": 1.0, "energy": 0.5},
    )
