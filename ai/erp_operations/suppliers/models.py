"""Supplier models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SupplierStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    PENDING = "pending"


class SupplierCategory(Enum):
    RAW_MATERIALS = "raw_materials"
    COMPONENTS = "components"
    SERVICES = "services"
    EQUIPMENT = "equipment"
    LOGISTICS = "logistics"


@dataclass
class Supplier:
    supplier_id: str
    name: str = ""
    category: SupplierCategory = SupplierCategory.RAW_MATERIALS
    status: SupplierStatus = SupplierStatus.ACTIVE
    contact_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    rating: float = 0.0
    lead_time_days: int = 0
    payment_terms: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SupplierContract:
    contract_id: str
    supplier_id: str = ""
    start_date: datetime | None = None
    end_date: datetime | None = None
    terms: str = ""
    total_value: float = 0.0
    status: str = "active"


@dataclass
class SupplierPerformance:
    performance_id: str
    supplier_id: str = ""
    period: str = ""
    on_time_delivery: float = 0.0
    quality_score: float = 0.0
    price_competitiveness: float = 0.0
    overall_score: float = 0.0
    issues: int = 0

    def calculate_overall(self) -> float:
        self.overall_score = (self.on_time_delivery + self.quality_score + self.price_competitiveness) / 3
        return self.overall_score
