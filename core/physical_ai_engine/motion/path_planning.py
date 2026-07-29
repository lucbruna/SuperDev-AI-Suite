from __future__ import annotations

import logging
import math
import uuid
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import MotionPlan

logger = logging.getLogger(__name__)


class PathPlanning:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def plan(self, robot_id: str, start: Dict[str, float], end: Dict[str, float], steps: int = 20) -> MotionPlan:
        waypoints = []
        total_dist = 0.0
        for i in range(steps + 1):
            t = i / steps
            wp = {
                "x": round(start.get("x", 0) + (end.get("x", 0) - start.get("x", 0)) * t, 2),
                "y": round(start.get("y", 0) + (end.get("y", 0) - start.get("y", 0)) * t, 2),
                "z": round(start.get("z", 0) + (end.get("z", 0) - start.get("z", 0)) * t, 2),
            }
            waypoints.append(wp)
            if i > 0:
                dx = waypoints[i]["x"] - waypoints[i - 1]["x"]
                dy = waypoints[i]["y"] - waypoints[i - 1]["y"]
                total_dist += math.sqrt(dx * dx + dy * dy)

        return MotionPlan(
            id=str(uuid.uuid4()),
            robot_id=robot_id,
            waypoints=waypoints,
            total_distance=round(total_dist, 2),
            estimated_time_seconds=round(total_dist / 0.5, 1),
            energy_estimate=round(total_dist * 0.15, 2),
            status="planned",
        )
