"""AI Animation Engine — character animation pillar (blueprint Volume 3).

Skeletal rigging (skeleton building, bone mapping, IK, pose optimisation),
facial animation (eyes, mouth, eyebrows, emotions, smile, blink, lip-sync)
and motion clips (walk, run, jump, gestures, body language, idle,
transitions and a motion library).
"""
from modules.ai_video_studio.ai_animation.animation_engine import AnimationEngine, get_animation_engine
from modules.ai_video_studio.ai_animation.animation_scheduler import AnimationScheduler, get_animation_scheduler
from modules.ai_video_studio.ai_animation.animation_optimizer import AnimationOptimizer, get_animation_optimizer
from modules.ai_video_studio.ai_animation.animation_learning import AnimationLearning, get_animation_learning
from modules.ai_video_studio.ai_animation.animation_statistics import AnimationStatistics, get_animation_statistics

__all__ = [
    "AnimationEngine",
    "get_animation_engine",
    "AnimationScheduler",
    "get_animation_scheduler",
    "AnimationOptimizer",
    "get_animation_optimizer",
    "AnimationLearning",
    "get_animation_learning",
    "AnimationStatistics",
    "get_animation_statistics",
]
