"""Avatar Training — learning, personalization and validation.

Learning modules (identity, speech, gesture, facial, movement) record
feedback; personalization adapts avatars; reinforcement learning picks
actions by reward; quality validation scores outputs; model versioning
tracks learned state versions.
"""
from modules.ai_video_studio.ai_avatar_engine.training.training_engine import (
    TrainingEngine,
    get_training_engine,
)

__all__ = ["TrainingEngine", "get_training_engine"]
