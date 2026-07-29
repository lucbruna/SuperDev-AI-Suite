from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import MotionPlan

logger = logging.getLogger(__name__)


class MovementControl:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._active_movements: Dict[str, str] = {}

    async def execute(self, robot_id: str, plan: MotionPlan) -> Dict[str, Any]:
        self._active_movements[robot_id] = "moving"
        logger.info(f"Robot {robot_id} executing movement: {plan.total_distance}m")
        await asyncio.sleep(0.1)
        self._active_movements[robot_id] = "completed"
        return {
            "robot_id": robot_id,
            "status": "completed",
            "distance": plan.total_distance,
            "time_seconds": plan.estimated_time_seconds,
            "energy_used": plan.energy_estimate,
        }

    def stop(self, robot_id: str) -> bool:
        if robot_id in self._active_movements:
            self._active_movements[robot_id] = "stopped"
            return True
        return False

    def get_status(self, robot_id: str) -> str:
        return self._active_movements.get(robot_id, "idle")
