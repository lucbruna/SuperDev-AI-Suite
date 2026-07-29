from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import EnvironmentData

logger = logging.getLogger(__name__)


class EnvironmentModel:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._data = EnvironmentData()

    def get_state(self) -> Dict[str, Any]:
        return {
            "temperature": self._data.temperature,
            "humidity": self._data.humidity,
            "pressure": self._data.pressure,
            "lighting": self._data.lighting_lux,
            "noise": self._data.noise_db,
            "air_quality": self._data.air_quality,
            "vibration": self._data.vibration,
        }

    def update(self, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            if hasattr(self._data, key):
                setattr(self._data, key, value)

    def simulate_conditions(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        temp_delta = scenario.get("temperature_delta", 0)
        self._data.temperature += temp_delta
        return self.get_state()
