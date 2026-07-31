"""Business Intelligence Marketing subsystem."""

from .engine import MarketingEngine
from .models import (
    Campaign,
    CampaignStatus,
    ChannelType,
    ConversionEvent,
    Lead,
    MarketingMetrics,
    Segment,
)

__all__ = [
    "CampaignStatus",
    "ChannelType",
    "Campaign",
    "Lead",
    "ConversionEvent",
    "MarketingMetrics",
    "Segment",
    "MarketingEngine",
]
