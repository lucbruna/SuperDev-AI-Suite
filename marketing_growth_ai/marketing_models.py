"""
Data models for Marketing Growth AI
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(Enum):
    AWARENESS = "awareness"
    ACQUISITION = "acquisition"
    RETENTION = "retention"
    REACTIVATION = "reactivation"
    PRODUCT_LAUNCH = "product_launch"
    SEASONAL = "seasonal"
    REFERRAL = "referral"


class Channel(Enum):
    GOOGLE_SEARCH = "google_search"
    GOOGLE_DISPLAY = "google_display"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    AFFILIATE = "affiliate"
    REFERRAL = "referral"
    ORGANIC = "organic"
    DIRECT = "direct"


class TrendDirection(Enum):
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


class ContentType(Enum):
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    EMAIL = "email"
    AD_COPY = "ad_copy"
    LANDING_PAGE = "landing_page"
    VIDEO_SCRIPT = "video_script"
    WHITEPAPER = "whitepaper"
    CASE_STUDY = "case_study"
    INFOGRAPHIC = "infographic"


class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass
class Campaign:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    type: CampaignType = CampaignType.ACQUISITION
    status: CampaignStatus = CampaignStatus.DRAFT
    objective: str = ""
    target_audience: Dict[str, Any] = field(default_factory=dict)
    channels: List[Channel] = field(default_factory=list)
    budget: float = 0.0
    spent: float = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CustomerSegment:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    criteria: Dict[str, Any] = field(default_factory=dict)
    size: int = 0
    ltv_estimate: float = 0.0
    churn_risk: float = 0.0
    preferred_channels: List[Channel] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MarketTrend:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    category: str = ""
    direction: TrendDirection = TrendDirection.STABLE
    strength: float = 0.0
    confidence: float = 0.0
    keywords: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    geographic_scope: str = "global"
    time_horizon_days: int = 90
    detected_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Competitor:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    domain: str = ""
    industry: str = ""
    estimated_traffic: int = 0
    keywords: List[str] = field(default_factory=list)
    ad_spend_estimate: float = 0.0
    social_followers: Dict[str, int] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    last_analyzed: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdvertisingMetrics:
    campaign_id: UUID
    date: datetime = field(default_factory=datetime.utcnow)
    impressions: int = 0
    clicks: int = 0
    cost: float = 0.0
    conversions: int = 0
    revenue: float = 0.0
    ctr: float = 0.0
    cpc: float = 0.0
    cpa: float = 0.0
    roas: float = 0.0
    roi: float = 0.0
    channel: Channel = Channel.GOOGLE_SEARCH


@dataclass
class ContentPiece:
    id: UUID = field(default_factory=uuid4)
    type: ContentType = ContentType.BLOG_POST
    title: str = ""
    body: str = ""
    keywords: List[str] = field(default_factory=list)
    target_audience: str = ""
    brand_voice: str = "professional"
    language: str = "pt-BR"
    status: str = "draft"
    seo_score: float = 0.0
    readability_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    performance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SEOKeyword:
    id: UUID = field(default_factory=uuid4)
    keyword: str = ""
    search_volume: int = 0
    difficulty: float = 0.0
    cpc: float = 0.0
    intent: str = "informational"
    current_position: Optional[int] = None
    target_position: int = 3
    competitor_positions: Dict[str, int] = field(default_factory=dict)
    related_keywords: List[str] = field(default_factory=list)
    content_gaps: List[str] = field(default_factory=list)
    last_checked: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SocialPost:
    id: UUID = field(default_factory=uuid4)
    platform: Channel = Channel.INSTAGRAM
    content: str = ""
    media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    metrics: Dict[str, int] = field(default_factory=dict)
    sentiment: Optional[Sentiment] = None
    engagement_rate: float = 0.0


@dataclass
class GrowthMetrics:
    period_start: datetime
    period_end: datetime
    total_users: int = 0
    new_users: int = 0
    active_users: int = 0
    churned_users: int = 0
    revenue: float = 0.0
    arr: float = 0.0
    mrr: float = 0.0
    ltv: float = 0.0
    cac: float = 0.0
    payback_period: float = 0.0


@dataclass
class AcquisitionMetrics:
    channel: Channel
    visitors: int = 0
    leads: int = 0
    customers: int = 0
    cost: float = 0.0
    cac: float = 0.0
    conversion_rate: float = 0.0
    lead_to_customer_rate: float = 0.0


@dataclass
class RetentionMetrics:
    cohort: str
    period: int
    users_start: int = 0
    users_retained: int = 0
    retention_rate: float = 0.0
    revenue_retained: float = 0.0
    churn_rate: float = 0.0


@dataclass
class MarketOpportunity:
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    category: str = ""
    estimated_value: float = 0.0
    effort_required: str = "medium"
    confidence: float = 0.0
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    recommended_actions: List[str] = field(default_factory=list)
    identified_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MarketingEvent:
    id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    campaign_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    channel: Optional[Channel] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    revenue: float = 0.0