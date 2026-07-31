"""Alert priority."""
from __future__ import annotations

from enum import Enum


class AlertPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class PriorityManager:
    def __init__(self) -> None:
        self._mapping: Dict[str, AlertPriority] = {}
    def set_priority(self, metric_name: str, priority: AlertPriority) -> None:
        self._mapping[metric_name] = priority
    def get_priority(self, metric_name: str) -> AlertPriority:
        return self._mapping.get(metric_name, AlertPriority.LOW)
    def remove_priority(self, metric_name: str) -> bool:
        if metric_name in self._mapping:
            del self._mapping[metric_name]
            return True
        return False
    def list_priorities(self) -> Dict[str, str]:
        return {k: v.value for k, v in self._mapping.items()}
