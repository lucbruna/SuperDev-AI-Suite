from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig

logger = logging.getLogger(__name__)


class SafetyManager:
    def __init__(self, config: PhysicalConfig):
        self._config = config
        self._zones: Dict[str, Dict[str, Any]] = {}
        self._incidents: List[Dict[str, Any]] = []

    def define_zone(self, zone_id: str, boundaries: Dict[str, float]) -> None:
        self._zones[zone_id] = {
            "boundaries": boundaries,
            "active": True,
        }

    def check_zone(self, robot_id: str, position: Dict[str, float]) -> bool:
        for zone_id, zone in self._zones.items():
            if zone["active"]:
                b = zone["boundaries"]
                if (b.get("x_min", -float("inf")) <= position.get("x", 0) <= b.get("x_max", float("inf"))
                        and b.get("y_min", -float("inf")) <= position.get("y", 0) <= b.get("y_max", float("inf"))):
                    self._incidents.append({
                        "id": str(uuid.uuid4()),
                        "robot_id": robot_id,
                        "zone": zone_id,
                        "position": position,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    logger.warning(f"Safety zone violation: {robot_id} in {zone_id}")
                    return False
        return True

    def get_incidents(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._incidents[-limit:]

    def get_safety_status(self) -> Dict[str, Any]:
        return {
            "zones": len(self._zones),
            "active_zones": sum(1 for z in self._zones.values() if z["active"]),
            "incidents": len(self._incidents),
            "safe": len(self._incidents) == 0,
        }
