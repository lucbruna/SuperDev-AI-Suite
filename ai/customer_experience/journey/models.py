"""Journey models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class JourneyStage(Enum):
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    PURCHASE = "purchase"
    RETENTION = "retention"
    ADVOCACY = "advocacy"


class TouchpointType(Enum):
    WEBSITE = "website"
    EMAIL = "email"
    SOCIAL = "social"
    AD = "ad"
    STORE = "store"
    SUPPORT = "support"
    REFERRAL = "referral"


@dataclass
class Touchpoint:
    touchpoint_id: str
    customer_id: str = ""
    touchpoint_type: TouchpointType = TouchpointType.WEBSITE
    channel: str = ""
    action: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LifecycleStage:
    stage: JourneyStage
    entered_at: datetime = field(default_factory=datetime.now)
    exited_at: datetime | None = None
    duration_days: float = 0.0
    conversion_rate: float = 0.0


@dataclass
class CustomerJourney:
    journey_id: str
    customer_id: str = ""
    current_stage: JourneyStage = JourneyStage.AWARENESS
    stages: list[LifecycleStage] = field(default_factory=list)
    touchpoints: list[Touchpoint] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    conversion_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class JourneyOptimization:
    optimization_id: str = ""
    stage: JourneyStage = JourneyStage.AWARENESS
    suggestion: str = ""
    expected_impact: float = 0.0
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)
