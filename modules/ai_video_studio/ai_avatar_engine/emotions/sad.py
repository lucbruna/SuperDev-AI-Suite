"""Sad emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="sad",
        facial={"smile": -0.5, "brow_raise": 0.2, "brow_frown": 0.4,
                "mouth_open": 0.1, "eye_open": 0.7, "blink": 0.2},
        body={"lean": -0.2, "arm_energy": 0.1, "posture": -0.5},
        voice={"pitch_shift": -2.0, "energy": 0.3},
    )
