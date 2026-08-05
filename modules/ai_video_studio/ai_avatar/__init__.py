"""AI Avatar & Digital Human Engine — virtual presenters (blueprint Volume 6).

Covers:
* Virtual actor library (2D + 3D, multiple art styles, genders, ages).
* Procedural character generation (unique presenters from a seed).
* Wardrobe (clothing + accessories per occasion).
* Emotional expressions (happy, sad, angry, surprised, fear...).
* Automatic gestures (point, wave, nod, shake, thumbs-up, shrug...).
* Body synchronization (speech + emotion + gesture → per-frame timeline).
* Facial & body capture (parameters from landmarks/keypoints/frames).
* Digital-human renderer (real MP4/PNG presenter output).
* Cross-cutting components: scheduler, optimizer, learning, statistics,
  memory, logger, history — matching the studio's architectural pattern.
"""
from modules.ai_video_studio.ai_avatar.avatar_engine import AvatarEngine, get_avatar_engine
from modules.ai_video_studio.ai_avatar.actor_library import ActorLibrary, VirtualActor, get_actor_library
from modules.ai_video_studio.ai_avatar.avatar_scheduler import AvatarScheduler, get_avatar_scheduler
from modules.ai_video_studio.ai_avatar.avatar_optimizer import AvatarOptimizer, get_avatar_optimizer
from modules.ai_video_studio.ai_avatar.avatar_learning import AvatarLearning, get_avatar_learning
from modules.ai_video_studio.ai_avatar.avatar_statistics import AvatarStatistics, get_avatar_statistics
from modules.ai_video_studio.ai_avatar.avatar_memory import AvatarMemory, get_avatar_memory
from modules.ai_video_studio.ai_avatar.avatar_logger import AvatarLogger, get_avatar_logger
from modules.ai_video_studio.ai_avatar.avatar_history import AvatarHistory, get_avatar_history
from modules.ai_video_studio.ai_avatar.character_generator import CharacterGenerator, CharacterSpec, get_character_generator
from modules.ai_video_studio.ai_avatar.wardrobe import Wardrobe, Outfit, get_wardrobe
from modules.ai_video_studio.ai_avatar.expression_engine import ExpressionEngine, Expression, get_expression_engine
from modules.ai_video_studio.ai_avatar.gesture_engine import GestureEngine, Gesture, get_gesture_engine
from modules.ai_video_studio.ai_avatar.body_sync import BodySync, get_body_sync
from modules.ai_video_studio.ai_avatar.facial_capture import FacialCapture, get_facial_capture
from modules.ai_video_studio.ai_avatar.digital_human import DigitalHumanRenderer, get_digital_human

__all__ = [
    "AvatarEngine",
    "get_avatar_engine",
    "ActorLibrary",
    "VirtualActor",
    "get_actor_library",
    "AvatarScheduler",
    "get_avatar_scheduler",
    "AvatarOptimizer",
    "get_avatar_optimizer",
    "AvatarLearning",
    "get_avatar_learning",
    "AvatarStatistics",
    "get_avatar_statistics",
    "AvatarMemory",
    "get_avatar_memory",
    "AvatarLogger",
    "get_avatar_logger",
    "AvatarHistory",
    "get_avatar_history",
    "CharacterGenerator",
    "CharacterSpec",
    "get_character_generator",
    "Wardrobe",
    "Outfit",
    "get_wardrobe",
    "ExpressionEngine",
    "Expression",
    "get_expression_engine",
    "GestureEngine",
    "Gesture",
    "get_gesture_engine",
    "BodySync",
    "get_body_sync",
    "FacialCapture",
    "get_facial_capture",
    "DigitalHumanRenderer",
    "get_digital_human",
]
