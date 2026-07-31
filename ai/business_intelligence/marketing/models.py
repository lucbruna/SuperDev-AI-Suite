"""Marketing models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CampaignStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ChannelType(Enum):
    EMAIL = "email"
    SOCIAL = "social"
    ADS = "ads"
    SEO = "seo"
    CONTENT = "content"
    SMS = "sms"
    PUSH = "push"


@dataclass
class Campaign:
    campaign_id: str
    name: str
    channel: ChannelType
    status: CampaignStatus = CampaignStatus.DRAFT
    budget: float = 0.0
    spent: float = 0.0
    start_date: datetime | None = None
    end_date: datetime | None = None
    target_audience: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def roi(self) -> float:
        return ((self.spent - self.budget) / self.budget * 100) if self.budget > 0 else 0.0

    @property
    def budget_utilization(self) -> float:
        return (self.spent / self.budget * 100) if self.budget > 0 else 0.0


@dataclass
class Lead:
    lead_id: str
    name: str
    email: str = ""
    source: str = ""
    score: float = 0.0
    status: str = "new"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionEvent:
    event_id: str
    lead_id: str
    campaign_id: str
    event_type: str = "conversion"
    value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MarketingMetrics:
    campaign_id: str
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0
    ctr: float = 0.0
    conversion_rate: float = 0.0
    cac: float = 0.0
    ltv: float = 0.0

    @property
    def roas(self) -> float:
        return (self.revenue / (self.impressions * 0.01)) if self.impressions > 0 else 0.0


@dataclass
class Segment:
    segment_id: str
    name: str
    criteria: dict[str, Any] = field(default_factory=dict)
    lead_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
