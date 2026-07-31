"""Sales models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class SalesOrderStatus(Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class QuotationStatus(Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class SalesOrder:
    order_id: str
    customer_id: str = ""
    items: List[Dict[str, Any]] = field(default_factory=list)
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    status: SalesOrderStatus = SalesOrderStatus.DRAFT
    sales_rep: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class Quotation:
    quotation_id: str
    customer_id: str = ""
    items: List[Dict[str, Any]] = field(default_factory=list)
    total: float = 0.0
    status: QuotationStatus = QuotationStatus.DRAFT
    valid_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class SalesTarget:
    target_id: str = ""
    sales_rep: str = ""
    period: str = ""
    target_amount: float = 0.0
    achieved: float = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @property
    def achievement_pct(self) -> float:
        return (self.achieved / self.target_amount * 100) if self.target_amount > 0 else 0.0


@dataclass
class Commission:
    commission_id: str = ""
    sales_rep: str = ""
    order_id: str = ""
    amount: float = 0.0
    rate: float = 0.0
    earned: float = 0.0
    period: str = ""
    paid: bool = False
