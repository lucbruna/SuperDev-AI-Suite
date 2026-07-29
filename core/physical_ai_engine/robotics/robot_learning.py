from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus

logger = logging.getLogger(__name__)


class RobotLearning:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._models: Dict[str, Dict[str, Any]] = {}

    def get_model(self, robot_id: str) -> Dict[str, Any]:
        if robot_id not in self._models:
            self._models[robot_id] = {
                "robot_id": robot_id,
                "tasks_learned": 0,
                "efficiency": 0.85,
                "improvement_rate": 0.02,
                "last_trained": None,
            }
        return self._models[robot_id]

    def record_training(self, robot_id: str, task_type: str, success: bool) -> None:
        model = self.get_model(robot_id)
        model["tasks_learned"] += 1
        if success:
            model["efficiency"] = min(1.0, model["efficiency"] + 0.01)
        else:
            model["efficiency"] = max(0.5, model["efficiency"] - 0.02)

    def get_all_models(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._models)
