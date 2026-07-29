from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import CollisionRisk, MotionPlan
from ..physical_security import PhysicalSecurityManager
from .path_planning import PathPlanning
from .movement_control import MovementControl
from .collision_detection import CollisionDetection

logger = logging.getLogger(__name__)


class MotionEngine:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext,
                 event_bus: PhysicalEventBus, security: PhysicalSecurityManager):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.security = security
        self.path: Optional[PathPlanning] = None
        self.movement: Optional[MovementControl] = None
        self.collision: Optional[CollisionDetection] = None

    async def initialize(self) -> None:
        self.path = PathPlanning(self.config, self.context, self.event_bus)
        self.movement = MovementControl(self.config, self.context, self.event_bus)
        self.collision = CollisionDetection(self.config, self.context, self.event_bus)
        logger.info("MotionEngine initialized")

    async def plan_path(self, robot_id: str, start: Dict[str, float], end: Dict[str, float]) -> MotionPlan:
        return self.path.plan(robot_id, start, end)

    async def execute_movement(self, robot_id: str, plan: MotionPlan) -> Dict[str, Any]:
        return await self.movement.execute(robot_id, plan)

    async def check_collision(self, robot_id: str, position: Dict[str, float]) -> CollisionRisk:
        return self.collision.check(robot_id, position)

    async def shutdown(self) -> None:
        logger.info("MotionEngine shutdown")
