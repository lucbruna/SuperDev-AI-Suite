from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import Robot, RobotStatus, RobotTask
from ..physical_security import PhysicalSecurityManager
from .robot_controller import RobotController
from .task_planner import TaskPlanner
from .robot_navigation import RobotNavigation
from .robot_learning import RobotLearning

logger = logging.getLogger(__name__)


class RoboticsEngine:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext,
                 event_bus: PhysicalEventBus, security: PhysicalSecurityManager):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.security = security
        self.controller: Optional[RobotController] = None
        self.planner: Optional[TaskPlanner] = None
        self.navigation: Optional[RobotNavigation] = None
        self.learning: Optional[RobotLearning] = None

    async def initialize(self) -> None:
        self.controller = RobotController(self.config, self.context, self.event_bus)
        self.planner = TaskPlanner(self.config, self.context, self.event_bus)
        self.navigation = RobotNavigation(self.config, self.context, self.event_bus)
        self.learning = RobotLearning(self.config, self.context, self.event_bus)
        logger.info("RoboticsEngine initialized")

    async def get_all(self) -> List[Robot]:
        return self.controller.get_all()

    async def get(self, robot_id: str) -> Optional[Robot]:
        return self.controller.get(robot_id)

    async def send_command(self, robot_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self.controller.command(robot_id, command, params)

    async def assign_task(self, robot_id: str, task: RobotTask) -> RobotTask:
        return await self.planner.assign(robot_id, task)

    async def navigate(self, robot_id: str, target: Dict[str, float]) -> Dict[str, Any]:
        return await self.navigation.navigate(robot_id, target)

    async def get_learning_model(self, robot_id: str) -> Dict[str, Any]:
        return self.learning.get_model(robot_id)

    async def shutdown(self) -> None:
        logger.info("RoboticsEngine shutdown")
