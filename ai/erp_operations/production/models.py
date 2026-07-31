"""Production models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


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
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
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
    last_maintenance: Optional[datetime] = None

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
    components: List[Dict[str, Any]] = field(default_factory=list)
    total_cost: float = 0.0
    version: str = "1.0"
    status: str = "active"
