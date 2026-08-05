"""Happy emotion preset."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset


def preset() -> EmotionPreset:
    return EmotionPreset(
        name="happy",
        facial={"smile": 0.8, "brow_raise": 0.3, "brow_frown": 0.0,
                "mouth_open": 0.25, "eye_open": 0.95, "cheek_raise": 0.5},
        body={"lean": 0.1, "arm_energy": 0.7, "posture": 0.4},
        voice={"pitch_shift": 2.0, "energy": 0.8},
    )
