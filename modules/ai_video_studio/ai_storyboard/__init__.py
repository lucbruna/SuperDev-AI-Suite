"""AI Storyboard — visual storyboarding for scenes, layouts and previews.

Implements the "storyboard" pillar of the studio (blueprint Volume 2).
"""
from modules.ai_video_studio.ai_storyboard.storyboard_engine import StoryboardEngine
from modules.ai_video_studio.ai_storyboard.storyboard_manager import StoryboardManager
from modules.ai_video_studio.ai_storyboard.storyboard_optimizer import StoryboardOptimizer
from modules.ai_video_studio.ai_storyboard.storyboard_learning import StoryboardLearning

__all__ = [
    "StoryboardEngine",
    "StoryboardManager",
    "StoryboardOptimizer",
    "StoryboardLearning",
]
