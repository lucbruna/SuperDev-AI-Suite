"""Excitement emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="excitement",
        facial={"smile": 0.9, "brow_raise": 0.7, "brow_frown": 0.0,
                "mouth_open": 0.5, "eye_open": 1.0, "cheek_raise": 0.6},
        body={"lean": 0.4, "arm_energy": 1.0, "posture": 0.7},
        voice={"pitch_shift": 3.5, "energy": 1.0},
    )
