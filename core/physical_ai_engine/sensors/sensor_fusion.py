from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import SensorReading

logger = logging.getLogger(__name__)


class SensorFusion:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def fuse(self, readings: List[SensorReading]) -> Dict[str, Any]:
        if not readings:
            return {"fused": False, "readings": 0}
        values = [r.value for r in readings]
        return {
            "fused": True,
            "readings": len(readings),
            "average": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "range": max(values) - min(values),
            "sensors": [r.sensor_id for r in readings],
        }

    def weighted_fusion(self, readings: List[SensorReading], weights: List[float]) -> float:
        if not readings or len(readings) != len(weights):
            return 0.0
        weighted_sum = sum(r.value * w for r, w in zip(readings, weights))
        return weighted_sum / sum(weights) if sum(weights) > 0 else 0.0
