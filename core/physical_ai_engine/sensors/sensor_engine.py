from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import AlertLevel, PhysicalAlert, SensorConfig, SensorReading, SensorType
from ..physical_security import PhysicalSecurityManager
from .data_reader import DataReader
from .calibration import Calibration
from .anomaly_detection import AnomalyDetection
from .sensor_fusion import SensorFusion

logger = logging.getLogger(__name__)


class SensorEngine:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext,
                 event_bus: PhysicalEventBus, security: PhysicalSecurityManager):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.security = security
        self.reader: Optional[DataReader] = None
        self.calibration: Optional[Calibration] = None
        self.anomaly: Optional[AnomalyDetection] = None
        self.fusion: Optional[SensorFusion] = None
        self._alerts: List[PhysicalAlert] = []

    async def initialize(self) -> None:
        self.reader = DataReader(self.config, self.context, self.event_bus)
        self.calibration = Calibration(self.config, self.context, self.event_bus)
        self.anomaly = AnomalyDetection(self.config, self.context, self.event_bus)
        self.fusion = SensorFusion(self.config, self.context, self.event_bus)
        logger.info("SensorEngine initialized")

    async def get_readings(self, sensor_id: str, count: int = 10) -> List[SensorReading]:
        return self.reader.get_readings(sensor_id, count)

    async def get_latest(self, sensor_id: str) -> Optional[SensorReading]:
        return self.reader.get_latest(sensor_id)

    async def calibrate_sensor(self, sensor_id: str) -> bool:
        return self.calibration.calibrate(sensor_id)

    async def detect_anomalies(self, sensor_id: str) -> List[Dict[str, Any]]:
        readings = self.reader.get_readings(sensor_id, 50)
        return self.anomaly.detect(readings)

    async def fuse_sensors(self, sensor_ids: List[str]) -> Dict[str, Any]:
        readings = []
        for sid in sensor_ids:
            r = self.reader.get_latest(sid)
            if r:
                readings.append(r)
        return self.fusion.fuse(readings)

    async def get_alerts(self) -> List[PhysicalAlert]:
        return self._alerts

    async def shutdown(self) -> None:
        logger.info("SensorEngine shutdown")
