from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import Robot, RobotStatus, RobotType

logger = logging.getLogger(__name__)


class RobotController:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._robots: Dict[str, Robot] = {}
        self._init_fleet()

    def _init_fleet(self) -> None:
        for i in range(1, 6):
            robot = Robot(
                id=f"R-{i:03d}",
                name=f"Robô {i}",
                robot_type=list(RobotType)[i % len(list(RobotType))],
                status=RobotStatus.IDLE,
                position={"x": i * 2.0, "y": i * 1.5, "z": 0},
                battery_level=85.0 + i * 2,
                connected=True,
            )
            self._robots[robot.id] = robot

    def get(self, robot_id: str) -> Optional[Robot]:
        return self._robots.get(robot_id)

    def get_all(self) -> List[Robot]:
        return list(self._robots.values())

    async def command(self, robot_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        robot = self._robots.get(robot_id)
        if not robot:
            return {"status": "error", "message": "Robot not found"}
        robot.status = RobotStatus.WORKING
        robot.last_heartbeat = datetime.utcnow()
        await self.event_bus.publish(PhysicalEvent(
            event_type=EventType.ROBOT_STATUS_CHANGED,
            payload={"robot_id": robot_id, "status": "working", "command": command},
        ))
        return {"status": "executed", "robot_id": robot_id, "command": command}

    def update_status(self, robot_id: str, status: RobotStatus) -> Optional[Robot]:
        robot = self._robots.get(robot_id)
        if robot:
            robot.status = status
            robot.last_heartbeat = datetime.utcnow()
        return robot

    def get_by_status(self, status: RobotStatus) -> List[Robot]:
        return [r for r in self._robots.values() if r.status == status]

    def get_available(self) -> List[Robot]:
        return [r for r in self._robots.values() if r.status == RobotStatus.IDLE]
