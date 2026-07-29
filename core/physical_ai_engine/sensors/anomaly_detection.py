from __future__ import annotations

import logging
import statistics
import uuid
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import SensorReading

logger = logging.getLogger(__name__)


class AnomalyDetection:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def detect(self, readings: List[SensorReading]) -> List[Dict[str, Any]]:
        if len(readings) < 3:
            return []
        values = [r.value for r in readings]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 1.0
        threshold = self.config.sensors.anomaly_threshold
        anomalies = []
        for r in readings:
            z_score = abs((r.value - mean) / stdev) if stdev > 0 else 0
            if z_score > threshold:
                anomalies.append({
                    "id": str(uuid.uuid4()),
                    "sensor_id": r.sensor_id,
                    "value": r.value,
                    "expected": mean,
                    "z_score": round(z_score, 2),
                    "severity": "high" if z_score > threshold * 1.5 else "medium",
                })
        return anomalies

    def get_threshold(self) -> float:
        return self.config.sensors.anomaly_threshold
