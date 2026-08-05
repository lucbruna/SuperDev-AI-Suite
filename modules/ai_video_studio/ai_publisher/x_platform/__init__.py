"""AI Publisher — X (Twitter) publishing and trends (Volume 7)."""
from __future__ import annotations

from modules.ai_video_studio.ai_publisher.x_platform.x_client import XClient, get_x_client
from modules.ai_video_studio.ai_publisher.x_platform.x_auth import XAuth, get_x_auth
from modules.ai_video_studio.ai_publisher.x_platform.x_upload import XUpload, get_x_upload
from modules.ai_video_studio.ai_publisher.x_platform.x_scheduler import XScheduler, get_x_scheduler
from modules.ai_video_studio.ai_publisher.x_platform.x_analytics import XAnalytics, get_x_analytics
from modules.ai_video_studio.ai_publisher.x_platform.x_hashtags import XHashtags, get_x_hashtags
from modules.ai_video_studio.ai_publisher.x_platform.x_trends import XTrends, get_x_trends
from modules.ai_video_studio.ai_publisher.x_platform.x_optimizer import XOptimizer, get_x_optimizer

__all__ = [
    "XClient",
    "get_x_client",
    "XAuth",
    "get_x_auth",
    "XUpload",
    "get_x_upload",
    "XScheduler",
    "get_x_scheduler",
    "XAnalytics",
    "get_x_analytics",
    "XHashtags",
    "get_x_hashtags",
    "XTrends",
    "get_x_trends",
    "XOptimizer",
    "get_x_optimizer",
]
