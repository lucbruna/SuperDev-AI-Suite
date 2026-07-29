from __future__ import annotations

import logging
import math
import uuid
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import CollisionRisk

logger = logging.getLogger(__name__)

OBSTACLES = [
    {"id": "OBS-001", "position": {"x": 5.0, "y": 3.0, "z": 0}, "radius": 0.5},
    {"id": "OBS-002", "position": {"x": 8.0, "y": 6.0, "z": 0}, "radius": 0.8},
    {"id": "OBS-003", "position": {"x": 12.0, "y": 2.0, "z": 0}, "radius": 0.3},
]


class CollisionDetection:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def check(self, robot_id: str, position: Dict[str, float]) -> CollisionRisk:
        for obs in OBSTACLES:
            dx = position.get("x", 0) - obs["position"]["x"]
            dy = position.get("y", 0) - obs["position"]["y"]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < obs["radius"] + self.config.motion.safety_distance_m:
                risk = CollisionRisk(
                    id=str(uuid.uuid4()),
                    robot_id=robot_id,
                    obstacle_id=obs["id"],
                    distance=round(distance, 2),
                    probability=round(max(0, 1 - distance / (obs["radius"] + 1)), 2),
                    severity="high" if distance < 0.3 else "medium",
                    recommended_action="emergency_stop" if distance < 0.3 else "slow_down",
                )
                return risk
        return CollisionRisk(
            id=str(uuid.uuid4()),
            robot_id=robot_id,
            obstacle_id="",
            distance=100.0,
            probability=0.0,
            severity="none",
        )

    def get_obstacles(self) -> List[Dict[str, Any]]:
        return list(OBSTACLES)
