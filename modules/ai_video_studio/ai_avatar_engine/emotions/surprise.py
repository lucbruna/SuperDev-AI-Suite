"""Surprise emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="surprise",
        facial={"smile": 0.1, "brow_raise": 1.0, "brow_frown": 0.0,
                "mouth_open": 0.9, "eye_open": 1.0, "forehead_raise": 0.9},
        body={"lean": 0.2, "arm_energy": 0.5, "posture": 0.3},
        voice={"pitch_shift": 4.0, "energy": 0.85},
    )
