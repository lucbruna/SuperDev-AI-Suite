"""
Marketing Growth AI - Enterprise growth intelligence platform
"""

__version__ = "1.0.0"
__author__ = "Marketing Growth Team"

from marketing_growth_ai.marketing_engine import MarketingEngine
from marketing_growth_ai.growth_manager import GrowthManager
from marketing_growth_ai.market_context import MarketContext
from marketing_growth_ai.marketing_models import (
    Campaign,
    CampaignStatus,
    CampaignType,
    Channel,
    CustomerSegment,
    MarketTrend,
    AdvertisingMetrics,
    ContentPiece,
    SEOKeyword,
    SocialPost,
    GrowthMetrics,
    AcquisitionMetrics,
    RetentionMetrics,
)
from marketing_growth_ai.marketing_config import MarketingConfig

__all__ = [
    "MarketingEngine",
    "GrowthManager",
    "MarketContext",
    "Campaign",
    "CampaignStatus",
    "CampaignType",
    "Channel",
    "CustomerSegment",
    "MarketTrend",
    "AdvertisingMetrics",
    "ContentPiece",
    "SEOKeyword",
    "SocialPost",
    "GrowthMetrics",
    "AcquisitionMetrics",
    "RetentionMetrics",
    "MarketingConfig",
]