"""AI Avatar & Digital Human Engine — Volume 6 of the AI Video Studio.

Subsystems:

* core — engine, manager, registry, scheduler, optimizer, learning,
  statistics, cache, logger, profiles, permissions, metadata, export/import
* digital_humans — procedural body/face/feature generation
* facial_animation — rig, mesh, landmarks and per-feature controllers
* emotions — emotional expression presets and blending
* gestures — automatic gesture libraries by context
* motion_capture — pose estimation, retargeting, cleaning
* clothing — wardrobe, garments, materials and textures
* hairstyles — hairstyle catalogs and color engine
* library — domain-specific virtual actor libraries
* training — learning, personalization, validation and versioning
* speaking — avatar × voice-studio × lip-sync: narrated talking-presenter video

Everything follows the studio's architectural pattern (singleton accessors
``get_*``, numpy/PIL primitives, JSON-serializable results).
"""
from modules.ai_video_studio.ai_avatar_engine.avatar_engine import AvatarEngine, get_avatar_engine
from modules.ai_video_studio.ai_avatar_engine.avatar_manager import AvatarManager, get_avatar_manager
from modules.ai_video_studio.ai_avatar_engine.avatar_registry import AvatarRegistry, get_avatar_registry
from modules.ai_video_studio.ai_avatar_engine.avatar_scheduler import AvatarScheduler, get_avatar_scheduler
from modules.ai_video_studio.ai_avatar_engine.avatar_optimizer import AvatarOptimizer, get_avatar_optimizer
from modules.ai_video_studio.ai_avatar_engine.avatar_learning import AvatarLearning, get_avatar_learning
from modules.ai_video_studio.ai_avatar_engine.avatar_statistics import AvatarStatistics, get_avatar_statistics
from modules.ai_video_studio.ai_avatar_engine.avatar_cache import AvatarCache, get_avatar_cache
from modules.ai_video_studio.ai_avatar_engine.avatar_logger import AvatarLogger, get_avatar_logger
from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile, profile_from_dict
from modules.ai_video_studio.ai_avatar_engine.avatar_permissions import AvatarPermissions, get_avatar_permissions
from modules.ai_video_studio.ai_avatar_engine.avatar_metadata import AvatarMetadata, get_avatar_metadata
from modules.ai_video_studio.ai_avatar_engine.avatar_export import AvatarExport, get_avatar_export
from modules.ai_video_studio.ai_avatar_engine.avatar_import import AvatarImport, get_avatar_import
from modules.ai_video_studio.ai_avatar_engine.speaking.speaking_engine import (
    SpeakingAvatarEngine,
    compose_facial,
    get_speaking_engine,
)

__all__ = [
    "AvatarEngine", "get_avatar_engine",
    "AvatarManager", "get_avatar_manager",
    "AvatarRegistry", "get_avatar_registry",
    "AvatarScheduler", "get_avatar_scheduler",
    "AvatarOptimizer", "get_avatar_optimizer",
    "AvatarLearning", "get_avatar_learning",
    "AvatarStatistics", "get_avatar_statistics",
    "AvatarCache", "get_avatar_cache",
    "AvatarLogger", "get_avatar_logger",
    "AvatarProfile", "profile_from_dict",
    "AvatarPermissions", "get_avatar_permissions",
    "AvatarMetadata", "get_avatar_metadata",
    "AvatarExport", "get_avatar_export",
    "AvatarImport", "get_avatar_import",
    "SpeakingAvatarEngine", "get_speaking_engine", "compose_facial",
]
