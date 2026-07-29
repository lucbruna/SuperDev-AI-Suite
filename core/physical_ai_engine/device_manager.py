from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .physical_models import Device, DeviceType, DeviceProtocol, TelemetryData

logger = logging.getLogger(__name__)


class DeviceManager:
    def __init__(self):
        self._devices: Dict[str, Device] = {}
        self._telemetry: Dict[str, List[TelemetryData]] = {}

    def register(self, name: str, device_type: DeviceType = DeviceType.GENERIC,
                 protocol: DeviceProtocol = DeviceProtocol.MQTT, location: str = "") -> Device:
        device = Device(
            id=str(uuid.uuid4()),
            name=name,
            device_type=device_type,
            protocol=protocol,
            location=location,
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
        device.last_seen = datetime.utcnow()
        return device

    def remove(self, device_id: str) -> bool:
        return bool(self._devices.pop(device_id, None))

    def list_by_type(self, device_type: DeviceType) -> List[Device]:
        return [d for d in self._devices.values() if d.device_type == device_type]

    def list_by_location(self, location: str) -> List[Device]:
        return [d for d in self._devices.values() if d.location == location]

    def get_all(self) -> List[Device]:
        return list(self._devices.values())

    def record_telemetry(self, device_id: str, metrics: Dict[str, float]) -> Optional[TelemetryData]:
        device = self._devices.get(device_id)
        if not device:
            return None
        data = TelemetryData(device_id=device_id, metrics=metrics)
        if device_id not in self._telemetry:
            self._telemetry[device_id] = []
        self._telemetry[device_id].append(data)
        if len(self._telemetry[device_id]) > 10000:
            self._telemetry[device_id].pop(0)
        device.last_seen = datetime.utcnow()
        return data

    def get_telemetry(self, device_id: str, limit: int = 100) -> List[TelemetryData]:
        return (self._telemetry.get(device_id, [])[-limit:])

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

    def get_connected_count(self) -> int:
        return sum(1 for d in self._devices.values() if d.status == "connected")

    def count_by_type(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for d in self._devices.values():
            counts[d.device_type.value] = counts.get(d.device_type.value, 0) + 1
        return counts
