"""Inventory models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class StockStatus(Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    OVERSTOCKED = "overstocked"


class MovementType(Enum):
    IN = "in"
    OUT = "out"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"


@dataclass
class InventoryItem:
    item_id: str
    product_id: str = ""
    name: str = ""
    sku: str = ""
    quantity: int = 0
    min_quantity: int = 0
    max_quantity: int = 1000
    location: str = ""
    cost: float = 0.0
    status: StockStatus = StockStatus.IN_STOCK
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def days_of_stock(self) -> float:
        return float(self.quantity) if self.quantity > 0 else 0.0


@dataclass
class StockMovement:
    movement_id: str
    item_id: str = ""
    movement_type: MovementType = MovementType.IN
    quantity: int = 0
    from_location: str = ""
    to_location: str = ""
    reference: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class ReplenishmentAlert:
    alert_id: str
    item_id: str = ""
    current_quantity: int = 0
    min_required: int = 0
    suggested_order: int = 0
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)
