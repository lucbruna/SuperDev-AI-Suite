"""Device Engine - Core device management for mobile/edge."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DeviceStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOST = "lost"
    STOLEN = "stolen"
    MAINTENANCE = "maintenance"


@dataclass
class ManagedDevice:
    device_id: str
    name: str
    status: DeviceStatus = DeviceStatus.ACTIVE
    platform: str = ""
    os_version: str = ""
    last_seen: datetime | None = None
    registered_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


class DeviceEngine:
    def __init__(self):
        self.devices: dict[str, ManagedDevice] = {}

    def register(self, name: str, platform: str = "", os_version: str = "") -> ManagedDevice:
        device_id = hashlib.sha256(f"{name}{platform}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        device = ManagedDevice(device_id=device_id, name=name, platform=platform, os_version=os_version)
        self.devices[device_id] = device
        return device

    def get(self, device_id: str) -> ManagedDevice | None:
        return self.devices.get(device_id)

    def update_status(self, device_id: str, status: DeviceStatus) -> bool:
        device = self.devices.get(device_id)
        if device:
            device.status = status
            return True
        return False

    def set_config(self, device_id: str, key: str, value: Any) -> bool:
        device = self.devices.get(device_id)
        if device:
            device.config[key] = value
            return True
        return False

    def add_tag(self, device_id: str, tag: str) -> bool:
        device = self.devices.get(device_id)
        if device and tag not in device.tags:
            device.tags.append(tag)
            return True
        return False

    def search(self, query: str) -> list[ManagedDevice]:
        return [
            d
            for d in self.devices.values()
            if query.lower() in d.name.lower() or any(query.lower() in t.lower() for t in d.tags)
        ]

    def list_devices(self, status: DeviceStatus = None) -> list[ManagedDevice]:
        if status:
            return [d for d in self.devices.values() if d.status == status]
        return list(self.devices.values())

    def count(self) -> int:
        return len(self.devices)
