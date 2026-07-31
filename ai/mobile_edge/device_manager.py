"""Device Manager - Enterprise device fleet management."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DeviceCategory(Enum):
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    NOTEBOOK = "notebook"
    DESKTOP = "desktop"
    IOT = "iot"
    INDUSTRIAL = "industrial"
    WEARABLE = "wearable"


class DeviceHealth(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


@dataclass
class DeviceRecord:
    device_id: str
    name: str
    category: DeviceCategory
    platform: str = ""
    os_version: str = ""
    ip_address: str = ""
    health: DeviceHealth = DeviceHealth.HEALTHY
    last_seen: datetime | None = None
    registered_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    specs: dict[str, Any] = field(default_factory=dict)


class DeviceManager:
    def __init__(self):
        self.devices: dict[str, DeviceRecord] = {}
        self.groups: dict[str, list[str]] = {}
        self.health_history: dict[str, list[dict[str, Any]]] = {}

    def register_device(self, name: str, category: DeviceCategory, **kwargs) -> DeviceRecord:
        device_id = hashlib.sha256(f"{name}{category.value}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        device = DeviceRecord(device_id=device_id, name=name, category=category, **kwargs)
        self.devices[device_id] = device
        return device

    def get_device(self, device_id: str) -> DeviceRecord | None:
        return self.devices.get(device_id)

    def update_health(self, device_id: str, health: DeviceHealth, message: str = "") -> bool:
        device = self.devices.get(device_id)
        if device:
            device.health = health
            device.last_seen = datetime.now()
            self.health_history.setdefault(device_id, []).append({"health": health.value, "message": message, "timestamp": datetime.now().isoformat()})
            return True
        return False

    def create_group(self, group_name: str) -> None:
        self.groups[group_name] = []

    def add_to_group(self, group_name: str, device_id: str) -> bool:
        if group_name in self.groups and device_id in self.devices:
            self.groups[group_name].append(device_id)
            return True
        return False

    def get_group_devices(self, group_name: str) -> list[DeviceRecord]:
        device_ids = self.groups.get(group_name, [])
        return [self.devices[did] for did in device_ids if did in self.devices]

    def list_devices(self, category: DeviceCategory = None, health: DeviceHealth = None) -> list[DeviceRecord]:
        devices = list(self.devices.values())
        if category:
            devices = [d for d in devices if d.category == category]
        if health:
            devices = [d for d in devices if d.health == health]
        return devices

    def search_devices(self, query: str) -> list[DeviceRecord]:
        return [d for d in self.devices.values() if query.lower() in d.name.lower() or any(query.lower() in t.lower() for t in d.tags)]

    def get_health_history(self, device_id: str, limit: int = 100) -> list[dict[str, Any]]:
        return self.health_history.get(device_id, [])[-limit:]

    def count(self) -> int:
        return len(self.devices)
