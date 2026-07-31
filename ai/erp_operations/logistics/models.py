"""Logistics models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class ShipmentStatus(Enum):
    PENDING = "pending"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"


class CarrierType(Enum):
    AIR = "air"
    SEA = "sea"
    ROAD = "road"
    RAIL = "rail"
    COURIER = "courier"


@dataclass
class Shipment:
    shipment_id: str
    order_id: str = ""
    carrier: str = ""
    carrier_type: CarrierType = CarrierType.ROAD
    status: ShipmentStatus = ShipmentStatus.PENDING
    origin: str = ""
    destination: str = ""
    weight: float = 0.0
    cost: float = 0.0
    tracking_number: str = ""
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Route:
    route_id: str
    name: str = ""
    origin: str = ""
    destination: str = ""
    distance_km: float = 0.0
    estimated_hours: float = 0.0
    cost: float = 0.0
    waypoints: List[str] = field(default_factory=list)


@dataclass
class Carrier:
    carrier_id: str
    name: str = ""
    carrier_type: CarrierType = CarrierType.ROAD
    rating: float = 0.0
    cost_per_km: float = 0.0
    max_weight: float = 0.0
    on_time_rate: float = 0.0
    active: bool = True


@dataclass
class DeliveryProof:
    proof_id: str
    shipment_id: str = ""
    recipient: str = ""
    signature: str = ""
    photo_url: str = ""
    delivered_at: datetime = field(default_factory=datetime.now)
    notes: str = ""
