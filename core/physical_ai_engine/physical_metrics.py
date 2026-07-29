from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .physical_context import PhysicalContext

logger = logging.getLogger(__name__)


@dataclass
class PhysicalMetrics:
    robots_active: int = 0
    robots_idle: int = 0
    robots_error: int = 0
    devices_connected: int = 0
    sensors_active: int = 0
    total_production: int = 0
    defective_units: int = 0
    maintenance_scheduled: int = 0
    maintenance_overdue: int = 0
    alerts_active: int = 0
    simulations_running: int = 0
    digital_twins_active: int = 0
    uptime_hours: float = 0.0
    energy_consumption_kwh: float = 0.0
    efficiency_rate: float = 0.0
    last_updated: Optional[datetime] = None


class MetricsCollector:
    def __init__(self, context: PhysicalContext):
        self.context = context
        self.metrics = PhysicalMetrics()
        self._history: Dict[str, List[float]] = {}

    def update_robot_count(self, active: int, idle: int, error: int) -> None:
        self.metrics.robots_active = active
        self.metrics.robots_idle = idle
        self.metrics.robots_error = error
        self.metrics.last_updated = datetime.utcnow()

    def update_production(self, total: int, defective: int) -> None:
        self.metrics.total_production = total
        self.metrics.defective_units = defective
        self.metrics.last_updated = datetime.utcnow()

    def record_metric(self, key: str, value: float) -> None:
        if key not in self._history:
            self._history[key] = []
        self._history[key].append(value)
        if len(self._history[key]) > 1000:
            self._history[key].pop(0)

    def get_average(self, key: str, window: int = 100) -> float:
        values = self._history.get(key, [])
        if not values:
            return 0.0
        recent = values[-window:]
        return sum(recent) / len(recent)

    def get_all_metrics(self) -> Dict[str, Any]:
        return {
            "robots_active": self.metrics.robots_active,
            "robots_idle": self.metrics.robots_idle,
            "robots_error": self.metrics.robots_error,
            "devices_connected": self.metrics.devices_connected,
            "sensors_active": self.metrics.sensors_active,
            "total_production": self.metrics.total_production,
            "defective_rate": (self.metrics.defective_units / max(self.metrics.total_production, 1)) * 100,
            "maintenance_scheduled": self.metrics.maintenance_scheduled,
            "alerts_active": self.metrics.alerts_active,
            "efficiency_rate": self.metrics.efficiency_rate,
        }
