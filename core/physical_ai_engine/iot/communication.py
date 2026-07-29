from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus

logger = logging.getLogger(__name__)


class Communication:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._channels: Dict[str, bool] = {}

    def ping(self, device_id: str) -> bool:
        return self._channels.get(device_id, True)

    def send(self, device_id: str, data: Dict[str, Any]) -> bool:
        logger.info(f"Sending to {device_id}: {data}")
        return True

    def receive(self, device_id: str) -> Optional[Dict[str, Any]]:
        return {"device_id": device_id, "ack": True}

    def open_channel(self, device_id: str) -> bool:
        self._channels[device_id] = True
        return True

    def close_channel(self, device_id: str) -> bool:
        self._channels[device_id] = False
        return True

    def is_connected(self, device_id: str) -> bool:
        return self._channels.get(device_id, False)
