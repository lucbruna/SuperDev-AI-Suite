"""Recommendation models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class RecommendationType(Enum):
    PRODUCT = "product"
    CONTENT = "content"
    OFFER = "offer"
    CROSS_SELL = "cross_sell"
    UPSELL = "upsell"


class RecommendationStatus(Enum):
    PENDING = "pending"
    DISPLAYED = "displayed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ProductRecommendation:
    recommendation_id: str
    customer_id: str = ""
    product_id: str = ""
    product_name: str = ""
    score: float = 0.0
    reason: str = ""
    recommendation_type: RecommendationType = RecommendationType.PRODUCT
    status: RecommendationStatus = RecommendationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentRecommendation:
    recommendation_id: str
    customer_id: str = ""
    content_id: str = ""
    content_title: str = ""
    content_type: str = ""
    score: float = 0.0
    reason: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Offer:
    offer_id: str
    customer_id: str = ""
    offer_type: str = ""
    discount_percent: float = 0.0
    description: str = ""
    valid_until: Optional[datetime] = None
    accepted: bool = False
    created_at: datetime = field(default_factory=datetime.now)
