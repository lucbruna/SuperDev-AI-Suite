from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import Device, DeviceType, DeviceProtocol

logger = logging.getLogger(__name__)


class DeviceRegistry:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._devices: Dict[str, Device] = {}

    def register(self, name: str, device_type: str = "generic", protocol: str = "mqtt") -> Device:
        device = Device(
            id=str(uuid.uuid4()),
            name=name,
            device_type=DeviceType(device_type) if device_type in [e.value for e in DeviceType] else DeviceType.GENERIC,
            protocol=DeviceProtocol(protocol) if protocol in [e.value for e in DeviceProtocol] else DeviceProtocol.MQTT,
            status="registered",
            last_seen=datetime.utcnow(),
        )
        self._devices[device.id] = device
        return device

    def get(self, device_id: str) -> Optional[Device]:
        return self._devices.get(device_id)

    def update(self, device_id: str, updates: Dict[str, Any]) -> Optional[Device]:
        device = self._devices.get(device_id)
        if not device:
            return None
        for key, value in updates.items():
            if hasattr(device, key):
                setattr(device, key, value)
        return device

    def remove(self, device_id: str) -> bool:
        return bool(self._devices.pop(device_id, None))

    def get_all(self) -> List[Device]:
        return list(self._devices.values())

    def connect(self, device_id: str) -> bool:
        device = self._devices.get(device_id)
        if not device:
            return False
        device.status = "connected"
        device.last_seen = datetime.utcnow()
        return True

    def disconnect(self, device_id: str) -> bool:
        device = self._devices.get(device_id)
        if not device:
            return False
        device.status = "disconnected"
        return True

    def get_connected(self) -> List[Device]:
        return [d for d in self._devices.values() if d.status == "connected"]
