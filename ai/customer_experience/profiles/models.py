"""Profile models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SegmentType(Enum):
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    PSYCHOGRAPHIC = "psychographic"
    GEOGRAPHIC = "geographic"
    VALUE_BASED = "value_based"


class BehaviorPattern(Enum):
    FREQUENT_BUYER = "frequent_buyer"
    WINDOW_SHOPPER = "window_shopper"
    BARGAIN_HUNTER = "bargain_hunter"
    PREMIUM_BUYER = "premium_buyer"
    SEASONAL = "seasonal"
    DORMANT = "dormant"


@dataclass
class CustomerSegment:
    segment_id: str
    name: str
    segment_type: SegmentType = SegmentType.BEHAVIORAL
    criteria: dict[str, Any] = field(default_factory=dict)
    customer_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BehaviorEvent:
    event_id: str
    customer_id: str
    event_type: str = ""
    event_data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CustomerPreference:
    customer_id: str
    preference_key: str = ""
    preference_value: Any = None
    confidence: float = 0.0
    source: str = ""
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProfileInsight:
    insight_id: str
    customer_id: str
    insight_type: str = ""
    description: str = ""
    confidence: float = 0.0
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
