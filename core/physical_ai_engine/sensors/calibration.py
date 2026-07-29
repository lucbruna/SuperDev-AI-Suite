from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus

logger = logging.getLogger(__name__)


class Calibration:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._records: Dict[str, datetime] = {}

    def calibrate(self, sensor_id: str) -> bool:
        self._records[sensor_id] = datetime.utcnow()
        logger.info(f"Sensor {sensor_id} calibrated")
        return True

    def is_calibration_due(self, sensor_id: str) -> bool:
        last = self._records.get(sensor_id)
        if not last:
            return True
        return datetime.utcnow() - last > timedelta(days=self.config.sensors.calibration_interval_days)

    def days_since_calibration(self, sensor_id: str) -> int:
        last = self._records.get(sensor_id)
        if not last:
            return 9999
        return (datetime.utcnow() - last).days

    def get_all(self) -> Dict[str, datetime]:
        return dict(self._records)
