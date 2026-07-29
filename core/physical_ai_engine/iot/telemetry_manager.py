from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import TelemetryData

logger = logging.getLogger(__name__)


class TelemetryManager:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._data: Dict[str, List[TelemetryData]] = {}
        self._max_per_device = 10000

    def record(self, device_id: str, metrics: Dict[str, float]) -> Optional[TelemetryData]:
        data = TelemetryData(device_id=device_id, metrics=metrics)
        if device_id not in self._data:
            self._data[device_id] = []
        self._data[device_id].append(data)
        if len(self._data[device_id]) > self._max_per_device:
            self._data[device_id].pop(0)
        return data

    def get_history(self, device_id: str, limit: int = 100) -> List[TelemetryData]:
        return self._data.get(device_id, [])[-limit:]

    def get_latest(self, device_id: str) -> Optional[TelemetryData]:
        history = self._data.get(device_id, [])
        return history[-1] if history else None

    def get_average(self, device_id: str, metric_key: str, window: int = 10) -> float:
        history = self._data.get(device_id, [])
        if not history:
            return 0.0
        recent = [t.metrics.get(metric_key, 0) for t in history[-window:] if metric_key in t.metrics]
        return sum(recent) / len(recent) if recent else 0.0

    def get_all_device_ids(self) -> List[str]:
        return list(self._data.keys())

    def clear(self, device_id: Optional[str] = None) -> None:
        if device_id:
            self._data.pop(device_id, None)
        else:
            self._data.clear()
