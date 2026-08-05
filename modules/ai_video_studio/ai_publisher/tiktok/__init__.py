"""AI Publisher — TikTok publishing and trends (Volume 7)."""
from __future__ import annotations

from modules.ai_video_studio.ai_publisher.tiktok.tiktok_client import TikTokClient, get_tiktok_client
from modules.ai_video_studio.ai_publisher.tiktok.tiktok_upload import TikTokUpload, get_tiktok_upload
from modules.ai_video_studio.ai_publisher.tiktok.tiktok_scheduler import TikTokScheduler, get_tiktok_scheduler
from modules.ai_video_studio.ai_publisher.tiktok.tiktok_analytics import TikTokAnalytics, get_tiktok_analytics
from modules.ai_video_studio.ai_publisher.tiktok.tiktok_music import TikTokMusic, get_tiktok_music
from modules.ai_video_studio.ai_publisher.tiktok.tiktok_hashtags import TikTokHashtags, get_tiktok_hashtags
from modules.ai_video_studio.ai_publisher.tiktok.tiktok_trends import TikTokTrends, get_tiktok_trends
from modules.ai_video_studio.ai_publisher.tiktok.tiktok_optimizer import TikTokOptimizer, get_tiktok_optimizer

__all__ = [
    "TikTokClient",
    "get_tiktok_client",
    "TikTokUpload",
    "get_tiktok_upload",
    "TikTokScheduler",
    "get_tiktok_scheduler",
    "TikTokAnalytics",
    "get_tiktok_analytics",
    "TikTokMusic",
    "get_tiktok_music",
    "TikTokHashtags",
    "get_tiktok_hashtags",
    "TikTokTrends",
    "get_tiktok_trends",
    "TikTokOptimizer",
    "get_tiktok_optimizer",
]
