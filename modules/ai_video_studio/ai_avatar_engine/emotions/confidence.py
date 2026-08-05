"""Confidence emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="confidence",
        facial={"smile": 0.3, "brow_raise": 0.1, "brow_frown": 0.0,
                "mouth_open": 0.15, "eye_open": 0.95},
        body={"lean": 0.2, "arm_energy": 0.6, "posture": 0.8},
        voice={"pitch_shift": -0.5, "energy": 0.75},
    )
