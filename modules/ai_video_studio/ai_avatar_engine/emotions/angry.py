"""Angry emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="angry",
        facial={"smile": -0.4, "brow_raise": 0.1, "brow_frown": 0.9,
                "mouth_open": 0.2, "eye_open": 0.85, "nose_wrinkle": 0.6},
        body={"lean": 0.3, "arm_energy": 0.9, "posture": 0.6},
        voice={"pitch_shift": -1.0, "energy": 0.95},
    )
