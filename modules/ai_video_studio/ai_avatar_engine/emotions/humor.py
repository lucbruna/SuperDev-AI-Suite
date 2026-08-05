"""Humor emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="humor",
        facial={"smile": 0.7, "brow_raise": 0.5, "brow_frown": 0.0,
                "mouth_open": 0.35, "eye_open": 0.9, "cheek_raise": 0.4},
        body={"lean": -0.2, "arm_energy": 0.8, "posture": 0.5},
        voice={"pitch_shift": 2.5, "energy": 0.9},
    )
