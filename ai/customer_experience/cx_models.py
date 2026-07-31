"""CX Models — Core data models for customer experience and CRM."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CustomerStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"
    PROSPECT = "prospect"
    VIP = "vip"


class CustomerTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class InteractionType(Enum):
    EMAIL = "email"
    PHONE = "phone"
    CHAT = "chat"
    SOCIAL = "social"
    IN_PERSON = "in_person"
    WEBSITE = "website"
    MOBILE = "mobile"


class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SentimentType(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LoyaltyAction(Enum):
    EARN = "earn"
    REDEEM = "redeem"
    EXPIRE = "expire"
    BONUS = "bonus"
    TRANSFER = "transfer"


@dataclass
class Customer:
    customer_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    email: str = ""
    phone: str = ""
    company: str = ""
    status: CustomerStatus = CustomerStatus.ACTIVE
    tier: CustomerTier = CustomerTier.BRONZE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CustomerProfile:
    customer_id: str = ""
    segment: str = ""
    preferences: dict[str, Any] = field(default_factory=dict)
    behavior_score: float = 0.0
    purchase_frequency: float = 0.0
    avg_order_value: float = 0.0
    lifetime_value: float = 0.0
    churn_risk: float = 0.0
    preferred_channel: InteractionType = InteractionType.EMAIL
    last_analysis: datetime | None = None


@dataclass
class Interaction:
    interaction_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    customer_id: str = ""
    interaction_type: InteractionType = InteractionType.EMAIL
    subject: str = ""
    content: str = ""
    sentiment: SentimentType = SentimentType.NEUTRAL
    agent_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Ticket:
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    customer_id: str = ""
    subject: str = ""
    description: str = ""
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    assigned_to: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    resolution: str = ""
    satisfaction_score: float = 0.0
    tags: list[str] = field(default_factory=list)


@dataclass
class Lead:
    lead_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    customer_id: str = ""
    name: str = ""
    email: str = ""
    source: str = ""
    score: float = 0.0
    status: LeadStatus = LeadStatus.NEW
    value: float = 0.0
    probability: float = 0.0
    assigned_to: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expected_close: datetime | None = None


@dataclass
class Recommendation:
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    customer_id: str = ""
    item_id: str = ""
    item_name: str = ""
    score: float = 0.0
    reason: str = ""
    category: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    accepted: bool = False


@dataclass
class LoyaltyTransaction:
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    customer_id: str = ""
    action: LoyaltyAction = LoyaltyAction.EARN
    points: int = 0
    balance: int = 0
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    expiry_date: datetime | None = None


@dataclass
class JourneyStage:
    stage_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    order: int = 0
    touchpoints: list[str] = field(default_factory=list)
    conversion_rate: float = 0.0
    avg_duration_days: float = 0.0


@dataclass
class CustomerJourney:
    journey_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    customer_id: str = ""
    current_stage: str = ""
    stages_completed: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    conversion_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
