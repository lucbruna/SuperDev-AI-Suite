"""Disgust emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="disgust",
        facial={"smile": -0.6, "brow_raise": 0.1, "brow_frown": 0.7,
                "mouth_open": 0.3, "eye_open": 0.5, "nose_wrinkle": 0.9},
        body={"lean": -0.3, "arm_energy": 0.2, "posture": -0.3},
        voice={"pitch_shift": -1.5, "energy": 0.4},
    )
