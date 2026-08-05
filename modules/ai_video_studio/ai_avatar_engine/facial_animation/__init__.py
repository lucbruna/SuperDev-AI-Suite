"""Facial Animation — rig, mesh, landmarks and feature controllers.

Controllers (smile, lips, jaw, cheeks, nose, brows, forehead, blink, gaze)
each output normalized parameter deltas consumed by the facial engine to
produce per-frame facial parameter sets.
"""
from modules.ai_video_studio.ai_avatar_engine.facial_animation.facial_engine import (
    FacialEngine,
    get_facial_engine,
)

__all__ = ["FacialEngine", "get_facial_engine"]
