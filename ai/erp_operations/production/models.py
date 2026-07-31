"""Production models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ProductionStatus(Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class QualityStatus(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    REWORK = "rework"


@dataclass
class ProductionOrder:
    order_id: str
    product_id: str = ""
    quantity: int = 0
    status: ProductionStatus = ProductionStatus.PLANNED
    start_date: datetime | None = None
    end_date: datetime | None = None
    assigned_line: str = ""
    priority: int = 0
    notes: str = ""


@dataclass
class ProductionLine:
    line_id: str
    name: str = ""
    capacity: int = 0
    current_load: int = 0
    status: str = "available"
    efficiency: float = 0.0
    last_maintenance: datetime | None = None

    @property
    def utilization(self) -> float:
        return (self.current_load / self.capacity * 100) if self.capacity > 0 else 0.0


@dataclass
class QualityCheck:
    check_id: str
    order_id: str = ""
    inspector: str = ""
    status: QualityStatus = QualityStatus.PENDING
    score: float = 0.0
    defects: int = 0
    notes: str = ""
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class BOM:
    bom_id: str
    product_id: str = ""
    components: list[dict[str, Any]] = field(default_factory=list)
    total_cost: float = 0.0
    version: str = "1.0"
    status: str = "active"
