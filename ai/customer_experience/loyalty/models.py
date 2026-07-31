"""Loyalty models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class LoyaltyAction(Enum):
    EARN = "earn"
    REDEEM = "redeem"
    EXPIRE = "expire"
    BONUS = "bonus"
    TRANSFER = "transfer"


class RewardType(Enum):
    DISCOUNT = "discount"
    FREE_PRODUCT = "free_product"
    FREE_SHIPPING = "free_shipping"
    EXCLUSIVE_ACCESS = "exclusive_access"
    CASHBACK = "cashback"


@dataclass
class LoyaltyAccount:
    customer_id: str
    balance: int = 0
    total_earned: int = 0
    total_redeemed: int = 0
    tier: str = "bronze"
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class LoyaltyTransaction:
    transaction_id: str
    customer_id: str = ""
    action: LoyaltyAction = LoyaltyAction.EARN
    points: int = 0
    balance: int = 0
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Reward:
    reward_id: str
    name: str = ""
    reward_type: RewardType = RewardType.DISCOUNT
    points_cost: int = 0
    description: str = ""
    active: bool = True


@dataclass
class CustomerValue:
    customer_id: str = ""
    lifetime_value: float = 0.0
    avg_order_value: float = 0.0
    purchase_frequency: float = 0.0
    churn_risk: float = 0.0
    clv_score: float = 0.0
    calculated_at: datetime = field(default_factory=datetime.now)
