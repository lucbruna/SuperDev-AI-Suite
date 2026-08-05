"""AI Publisher — Social platform cross-management (Volume 7)."""
from __future__ import annotations

from modules.ai_video_studio.ai_publisher.social.social_manager import SocialManager, get_social_manager
from modules.ai_video_studio.ai_publisher.social.social_scheduler import SocialScheduler, get_social_scheduler
from modules.ai_video_studio.ai_publisher.social.social_analytics import SocialAnalytics, get_social_analytics
from modules.ai_video_studio.ai_publisher.social.social_profiles import SocialProfiles, get_social_profiles
from modules.ai_video_studio.ai_publisher.social.hashtag_generator import HashtagGenerator, get_hashtag_generator
from modules.ai_video_studio.ai_publisher.social.caption_generator import CaptionGenerator, get_caption_generator
from modules.ai_video_studio.ai_publisher.social.thumbnail_optimizer import ThumbnailOptimizer, get_thumbnail_optimizer
from modules.ai_video_studio.ai_publisher.social.engagement_predictor import EngagementPredictor, get_engagement_predictor

__all__ = [
    "SocialManager",
    "get_social_manager",
    "SocialScheduler",
    "get_social_scheduler",
    "SocialAnalytics",
    "get_social_analytics",
    "SocialProfiles",
    "get_social_profiles",
    "HashtagGenerator",
    "get_hashtag_generator",
    "CaptionGenerator",
    "get_caption_generator",
    "ThumbnailOptimizer",
    "get_thumbnail_optimizer",
    "EngagementPredictor",
    "get_engagement_predictor",
]
