from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType

logger = logging.getLogger(__name__)

KNOWN_DEFECTS = {
    "scratch": {"severity": "medium", "description": "Arranhão superficial detectado", "action": "inspecionar"},
    "denting": {"severity": "high", "description": "Amassado detectado na superfície", "action": "rejeitar"},
    "crack": {"severity": "critical", "description": "Trinca estrutural detectada", "action": "rejeitar imediatamente"},
    "discoloration": {"severity": "low", "description": "Variação de cor fora do padrão", "action": "reclassificar"},
    "deformation": {"severity": "high", "description": "Deformação geométrica detectada", "action": "rejeitar"},
}


class DefectDetection:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._detections: List[Dict[str, Any]] = []

    def analyze(self, camera_id: str, product_id: str) -> List[Dict[str, Any]]:
        defects = []
        for defect_type, info in KNOWN_DEFECTS.items():
            if hash(product_id + defect_type) % 5 == 0:
                detection = {
                    "id": str(uuid.uuid4()),
                    "camera_id": camera_id,
                    "product_id": product_id,
                    "defect_type": defect_type,
                    "severity": info["severity"],
                    "description": info["description"],
                    "recommended_action": info["action"],
                    "confidence": round(0.7 + (hash(defect_type) % 25) / 100, 2),
                }
                defects.append(detection)
                self._detections.append(detection)
                if info["severity"] == "critical":
                    import asyncio
                    asyncio.ensure_future(self.event_bus.publish(PhysicalEvent(
                        event_type=EventType.VISION_DEFECT_DETECTED,
                        payload=detection,
                    )))
        return defects

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self._detections)
        by_severity: Dict[str, int] = {}
        for d in self._detections:
            sev = d.get("severity", "unknown")
            by_severity[sev] = by_severity.get(sev, 0) + 1
        return {"total": total, "by_severity": by_severity}
