"""Purchases models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class PurchaseOrderStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"


@dataclass
class PurchaseOrderItem:
    product_id: str = ""
    name: str = ""
    quantity: int = 0
    unit_price: float = 0.0
    total: float = 0.0


@dataclass
class PurchaseOrder:
    po_id: str
    supplier_id: str = ""
    items: List[PurchaseOrderItem] = field(default_factory=list)
    total: float = 0.0
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    requested_by: str = ""
    approved_by: str = ""
    expected_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class PriceComparison:
    comparison_id: str = ""
    product_id: str = ""
    prices: Dict[str, float] = field(default_factory=dict)
    best_supplier: str = ""
    best_price: float = 0.0
    savings: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
