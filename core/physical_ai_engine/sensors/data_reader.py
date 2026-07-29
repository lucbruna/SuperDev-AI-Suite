from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import SensorReading, SensorType

logger = logging.getLogger(__name__)


class DataReader:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._sensors: Dict[str, List[SensorReading]] = {}
        self._init_readings()

    def _init_readings(self) -> None:
        import random
        for sensor_id in ["S-TEMP-001", "S-PRES-001", "S-VIB-001", "S-HUM-001", "S-CURR-001"]:
            self._sensors[sensor_id] = []
            base = random.uniform(20, 80)
            for i in range(100):
                self._sensors[sensor_id].append(SensorReading(
                    id=f"{sensor_id}-{i}",
                    sensor_id=sensor_id,
                    value=base + random.uniform(-5, 5),
                    timestamp=datetime.utcnow(),
                ))

    def get_readings(self, sensor_id: str, count: int = 10) -> List[SensorReading]:
        readings = self._sensors.get(sensor_id, [])
        return readings[-count:]

    def get_latest(self, sensor_id: str) -> Optional[SensorReading]:
        readings = self._sensors.get(sensor_id, [])
        return readings[-1] if readings else None

    def add_reading(self, sensor_id: str, value: float, sensor_type: SensorType = SensorType.TEMPERATURE) -> SensorReading:
        reading = SensorReading(
            id=str(uuid.uuid4()),
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            value=value,
        )
        if sensor_id not in self._sensors:
            self._sensors[sensor_id] = []
        self._sensors[sensor_id].append(reading)
        if len(self._sensors[sensor_id]) > 10000:
            self._sensors[sensor_id].pop(0)
        return reading

    def get_all_sensor_ids(self) -> List[str]:
        return list(self._sensors.keys())
