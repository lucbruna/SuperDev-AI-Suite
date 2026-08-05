"""Fear emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="fear",
        facial={"smile": -0.3, "brow_raise": 0.8, "brow_frown": 0.5,
                "mouth_open": 0.6, "eye_open": 1.0, "forehead_raise": 0.7},
        body={"lean": -0.4, "arm_energy": 0.3, "posture": -0.6},
        voice={"pitch_shift": 3.0, "energy": 0.6},
    )
