from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus

logger = logging.getLogger(__name__)


class CameraManager:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._cameras: Dict[str, Dict[str, Any]] = {
            "CAM-001": {"id": "CAM-001", "name": "Linha A - Inspeção", "resolution": "1920x1080", "fps": 30, "status": "active"},
            "CAM-002": {"id": "CAM-002", "name": "Linha B - Qualidade", "resolution": "3840x2160", "fps": 60, "status": "active"},
            "CAM-003": {"id": "CAM-003", "name": "Esteira - Segurança", "resolution": "1280x720", "fps": 15, "status": "active"},
        }

    def get(self, camera_id: str) -> Optional[Dict[str, Any]]:
        return self._cameras.get(camera_id)

    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._cameras.values())

    def activate(self, camera_id: str) -> bool:
        cam = self._cameras.get(camera_id)
        if cam:
            cam["status"] = "active"
            return True
        return False

    def deactivate(self, camera_id: str) -> bool:
        cam = self._cameras.get(camera_id)
        if cam:
            cam["status"] = "inactive"
            return True
        return False
