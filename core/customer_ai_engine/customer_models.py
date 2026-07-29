"""
Customer Models - Core customer experience data models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class CustomerTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SentimentType(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"
    SATISFIED = "satisfied"
    DISAPPOINTED = "disappointed"


class ChannelType(Enum):
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    EMAIL = "email"
    WEBSITE = "website"
    APP = "app"
    SOCIAL = "social"
    CHAT = "chat"


class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"


@dataclass
class Message:
    id: str
    content: str
    sender: str = "customer"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    channel: ChannelType = ChannelType.CHAT
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    id: str
    customer_id: str
    channel: ChannelType = ChannelType.CHAT
    messages: List[Message] = field(default_factory=list)
    intent: str = ""
    status: str = "active"
    satisfaction_score: float = 0.0
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


@dataclass
class CustomerProfile:
    id: str
    name: str
    email: str = ""
    phone: str = ""
    segments: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    tier: CustomerTier = CustomerTier.BRONZE
    total_spent: float = 0.0
    total_orders: int = 0
    last_purchase: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LeadScore:
    customer_id: str
    score: float = 0.0
    engagement_level: str = "low"
    purchase_intent: float = 0.0
    likelihood_to_buy: float = 0.0
    segment: str = ""
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Order:
    id: str
    customer_id: str
    items: List[Dict[str, Any]] = field(default_factory=list)
    total: float = 0.0
    status: str = "pending"
    channel: ChannelType = ChannelType.WEBSITE
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Ticket:
    id: str
    customer_id: str
    subject: str
    description: str = ""
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    category: str = ""
    assigned_to: str = ""
    resolution: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


@dataclass
class Recommendation:
    id: str
    customer_id: str
    product_id: str = ""
    product_name: str = ""
    category: str = ""
    score: float = 0.0
    reason: str = ""
    channel: ChannelType = ChannelType.WEBSITE
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SentimentResult:
    text: str
    sentiment: SentimentType = SentimentType.NEUTRAL
    score: float = 0.0
    confidence: float = 0.0
    emotions: Dict[str, float] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Feedback:
    id: str
    customer_id: str
    rating: int = 0
    comment: str = ""
    category: str = ""
    sentiment: SentimentType = SentimentType.NEUTRAL
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LoyaltyTier:
    customer_id: str
    tier: CustomerTier = CustomerTier.BRONZE
    points: int = 0
    points_to_next: int = 1000
    lifetime_value: float = 0.0
    join_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Reward:
    id: str
    customer_id: str
    name: str
    points_cost: int = 0
    description: str = ""
    expires_at: Optional[datetime] = None
    redeemed: bool = False


@dataclass
class Campaign:
    id: str
    name: str
    channel: ChannelType = ChannelType.EMAIL
    status: CampaignStatus = CampaignStatus.DRAFT
    target_segment: str = ""
    content: str = ""
    recipients_count: int = 0
    sent_count: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    conversion_rate: float = 0.0
    scheduled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Workflow:
    id: str
    name: str
    trigger: str = ""
    actions: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"
    execution_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CallRecord:
    id: str
    customer_id: str
    caller_number: str = ""
    duration_seconds: int = 0
    status: str = "completed"
    transcript: str = ""
    sentiment: SentimentType = SentimentType.NEUTRAL
    started_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CXAlert:
    id: str
    alert_type: str
    severity: str
    title: str
    message: str
    customer_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
