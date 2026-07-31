"""Accelerator - Hardware acceleration management."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class AcceleratorStatus(Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


@dataclass
class AcceleratorInfo:
    accelerator_id: str
    name: str
    type: str = "cpu"
    status: AcceleratorStatus = AcceleratorStatus.AVAILABLE
    compute_units: int = 1
    memory_mb: float = 0.0
    utilization: float = 0.0
    last_used: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AcceleratorManager:
    def __init__(self):
        self.accelerators: Dict[str, AcceleratorInfo] = {}

    def register(self, name: str, type: str = "cpu", compute_units: int = 1, memory_mb: float = 0.0) -> AcceleratorInfo:
        acc = AcceleratorInfo(accelerator_id=name, name=name, type=type, compute_units=compute_units, memory_mb=memory_mb)
        self.accelerators[name] = acc
        return acc

    def acquire(self, accelerator_id: str) -> bool:
        acc = self.accelerators.get(accelerator_id)
        if acc and acc.status == AcceleratorStatus.AVAILABLE:
            acc.status = AcceleratorStatus.IN_USE
            acc.last_used = datetime.now()
            return True
        return False

    def release(self, accelerator_id: str) -> bool:
        acc = self.accelerators.get(accelerator_id)
        if acc and acc.status == AcceleratorStatus.IN_USE:
            acc.status = AcceleratorStatus.AVAILABLE
            return True
        return False

    def get(self, accelerator_id: str) -> Optional[AcceleratorInfo]:
        return self.accelerators.get(accelerator_id)

    def list_available(self) -> List[AcceleratorInfo]:
        return [a for a in self.accelerators.values() if a.status == AcceleratorStatus.AVAILABLE]

    def count(self) -> int:
        return len(self.accelerators)
