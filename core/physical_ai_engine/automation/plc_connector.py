from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus

logger = logging.getLogger(__name__)


class PLCConnector:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._tags: Dict[str, Any] = {
            "production.speed": 100.0,
            "production.count": 50000,
            "production.defective": 250,
            "machine.temperature": 65.0,
            "machine.pressure": 150.0,
            "line.status": "running",
            "alarm.active": False,
        }

    def read(self, tag: str) -> Any:
        return self._tags.get(tag, None)

    def write(self, tag: str, value: Any) -> bool:
        if tag in self._tags:
            self._tags[tag] = value
            return True
        return False

    def read_batch(self, tags: List[str]) -> Dict[str, Any]:
        return {tag: self._tags.get(tag) for tag in tags}

    def write_batch(self, values: Dict[str, Any]) -> int:
        count = 0
        for tag, value in values.items():
            if self.write(tag, value):
                count += 1
        return count

    def list_tags(self) -> List[str]:
        return list(self._tags.keys())

    def is_connected(self) -> bool:
        return True
