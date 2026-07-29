from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import DeviceProtocol

logger = logging.getLogger(__name__)


class ProtocolAdapter:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def encode(self, protocol: DeviceProtocol, data: Dict[str, Any]) -> bytes:
        if protocol == DeviceProtocol.MQTT:
            return json.dumps(data).encode()
        return json.dumps(data).encode()

    def decode(self, protocol: DeviceProtocol, raw: bytes) -> Dict[str, Any]:
        if protocol == DeviceProtocol.MQTT:
            return json.loads(raw.decode())
        return json.loads(raw.decode())

    def translate(self, from_protocol: DeviceProtocol, to_protocol: DeviceProtocol, data: Dict[str, Any]) -> Dict[str, Any]:
        return data
