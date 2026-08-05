"""AI Video Studio — AI Marketing Studio (Volume 5).

Campaign generation (captions, hashtags, content ideas, schedule), platform
caption writing, hashtag suggestions and promo poster images. Real outputs
land under ``modules/downloads/marketing/``.
"""
from __future__ import annotations

from modules.ai_video_studio.ai_marketing.caption_generator import generate_caption
from modules.ai_video_studio.ai_marketing.hashtag_engine import generate_hashtags
from modules.ai_video_studio.ai_marketing.marketing_engine import MarketingEngine, get_marketing_engine
from modules.ai_video_studio.ai_marketing.poster_engine import generate_poster

__all__ = [
    "generate_caption",
    "generate_hashtags",
    "MarketingEngine",
    "get_marketing_engine",
    "generate_poster",
]
