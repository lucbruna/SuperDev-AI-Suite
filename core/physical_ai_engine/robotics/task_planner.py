from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import RobotTask

logger = logging.getLogger(__name__)


class TaskPlanner:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._tasks: Dict[str, RobotTask] = {}

    async def assign(self, robot_id: str, task: RobotTask) -> RobotTask:
        task.id = str(uuid.uuid4())
        task.robot_id = robot_id
        task.status = "assigned"
        task.started_at = datetime.utcnow()
        self._tasks[task.id] = task

        await self.event_bus.publish(PhysicalEvent(
            event_type=EventType.ROBOT_TASK_STARTED,
            payload={"robot_id": robot_id, "task_id": task.id, "task_type": task.task_type},
        ))
        return task

    async def complete(self, task_id: str) -> Optional[RobotTask]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        task.status = "completed"
        task.progress = 100.0
        task.completed_at = datetime.utcnow()

        await self.event_bus.publish(PhysicalEvent(
            event_type=EventType.ROBOT_TASK_COMPLETED,
            payload={"task_id": task_id, "robot_id": task.robot_id},
        ))
        return task

    def get_task(self, task_id: str) -> Optional[RobotTask]:
        return self._tasks.get(task_id)

    def get_robot_tasks(self, robot_id: str) -> List[RobotTask]:
        return [t for t in self._tasks.values() if t.robot_id == robot_id]

    def get_pending(self) -> List[RobotTask]:
        return [t for t in self._tasks.values() if t.status == "assigned"]
