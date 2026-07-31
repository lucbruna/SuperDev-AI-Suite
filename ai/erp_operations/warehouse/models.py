"""Warehouse models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class WarehouseZone(Enum):
    RECEIVING = "receiving"
    STORAGE = "storage"
    PICKING = "picking"
    PACKING = "packing"
    SHIPPING = "shipping"
    RETURNS = "returns"


class BinStatus(Enum):
    EMPTY = "empty"
    PARTIAL = "partial"
    FULL = "full"
    BLOCKED = "blocked"


@dataclass
class WarehouseZoneModel:
    zone_id: str
    name: str = ""
    zone_type: WarehouseZone = WarehouseZone.STORAGE
    capacity: int = 0
    current_usage: int = 0
    temperature_controlled: bool = False

    @property
    def utilization(self) -> float:
        return (self.current_usage / self.capacity * 100) if self.capacity > 0 else 0.0


@dataclass
class Bin:
    bin_id: str
    zone_id: str = ""
    aisle: str = ""
    rack: str = ""
    level: int = 0
    position: int = 0
    status: BinStatus = BinStatus.EMPTY
    product_id: str = ""
    quantity: int = 0
    max_capacity: int = 100


@dataclass
class PutAwayTask:
    task_id: str
    product_id: str = ""
    quantity: int = 0
    source_zone: str = ""
    target_bin: str = ""
    status: str = "pending"
    assigned_to: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PickTask:
    task_id: str
    order_id: str = ""
    product_id: str = ""
    quantity: int = 0
    bin_id: str = ""
    status: str = "pending"
    assigned_to: str = ""
    created_at: datetime = field(default_factory=datetime.now)
