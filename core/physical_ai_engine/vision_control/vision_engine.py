from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import VisionInspection
from ..physical_security import PhysicalSecurityManager
from .camera_manager import CameraManager
from .object_tracking import ObjectTracking
from .quality_inspection import QualityInspection
from .defect_detection import DefectDetection

logger = logging.getLogger(__name__)


class VisionEngine:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext,
                 event_bus: PhysicalEventBus, security: PhysicalSecurityManager):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.security = security
        self.cameras: Optional[CameraManager] = None
        self.tracking: Optional[ObjectTracking] = None
        self.quality: Optional[QualityInspection] = None
        self.defects: Optional[DefectDetection] = None

    async def initialize(self) -> None:
        self.cameras = CameraManager(self.config, self.context, self.event_bus)
        self.tracking = ObjectTracking(self.config, self.context, self.event_bus)
        self.quality = QualityInspection(self.config, self.context, self.event_bus)
        self.defects = DefectDetection(self.config, self.context, self.event_bus)
        logger.info("VisionEngine initialized")

    async def inspect(self, camera_id: str, product_id: str) -> Dict[str, Any]:
        inspection = self.quality.inspect(camera_id, product_id)
        if not inspection.passed:
            defects = self.defects.analyze(camera_id, product_id)
            return {"inspection": inspection, "defects": defects}
        return {"inspection": inspection, "defects": []}

    async def track_object(self, camera_id: str, object_id: str) -> Dict[str, Any]:
        return self.tracking.track(camera_id, object_id)

    async def get_camera(self, camera_id: str) -> Optional[Dict[str, Any]]:
        return self.cameras.get(camera_id)

    async def list_cameras(self) -> List[Dict[str, Any]]:
        return self.cameras.list_all()

    async def shutdown(self) -> None:
        logger.info("VisionEngine shutdown")
