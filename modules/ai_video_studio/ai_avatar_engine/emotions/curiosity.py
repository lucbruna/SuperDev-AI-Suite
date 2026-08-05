"""Curiosity emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="curiosity",
        facial={"smile": 0.1, "brow_raise": 0.7, "brow_frown": 0.1,
                "mouth_open": 0.15, "eye_open": 0.95, "head_tilt": 8.0},
        body={"lean": 0.5, "arm_energy": 0.4, "posture": 0.5},
        voice={"pitch_shift": 1.5, "energy": 0.6},
    )
