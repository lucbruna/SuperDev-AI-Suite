from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import VisionInspection

logger = logging.getLogger(__name__)


class QualityInspection:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._inspections: List[VisionInspection] = []

    def inspect(self, camera_id: str, product_id: str) -> VisionInspection:
        passed = hash(product_id) % 10 > 1
        inspection = VisionInspection(
            id=str(uuid.uuid4()),
            camera_id=camera_id,
            product_id=product_id,
            passed=passed,
            defects=[] if passed else ["scratch", "denting"],
            confidence=0.95 if passed else 0.82,
            processing_time_ms=45.0,
        )
        self._inspections.append(inspection)
        return inspection

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self._inspections)
        passed = sum(1 for i in self._inspections if i.passed)
        return {
            "total_inspections": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / max(total, 1)) * 100,
            "avg_confidence": sum(i.confidence for i in self._inspections) / max(total, 1),
        }

    def get_recent(self, limit: int = 50) -> List[VisionInspection]:
        return self._inspections[-limit:]
