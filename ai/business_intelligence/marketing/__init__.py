"""Business Intelligence Marketing subsystem."""
from .models import (
    CampaignStatus, ChannelType,
    Campaign, Lead, ConversionEvent, MarketingMetrics, Segment,
)
from .engine import MarketingEngine

__all__ = [
    "CampaignStatus", "ChannelType",
    "Campaign", "Lead", "ConversionEvent", "MarketingMetrics", "Segment",
    "MarketingEngine",
]
