"""Device Registry - Enterprise device registry."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class DeviceRegistration:
    registration_id: str
    device_id: str
    owner: str = ""
    department: str = ""
    location: str = ""
    ip_address: str = ""
    mac_address: str = ""
    certificates: List[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class DeviceRegistry:
    def __init__(self):
        self.registrations: Dict[str, DeviceRegistration] = {}
        self.by_device: Dict[str, str] = {}

    def register(self, device_id: str, owner: str = "", department: str = "", **kwargs) -> DeviceRegistration:
        reg_id = hashlib.sha256(f"{device_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        reg = DeviceRegistration(registration_id=reg_id, device_id=device_id, owner=owner, department=department, **kwargs)
        self.registrations[reg_id] = reg
        self.by_device[device_id] = reg_id
        return reg

    def get(self, registration_id: str) -> Optional[DeviceRegistration]:
        return self.registrations.get(registration_id)

    def get_by_device(self, device_id: str) -> Optional[DeviceRegistration]:
        reg_id = self.by_device.get(device_id)
        return self.registrations.get(reg_id) if reg_id else None

    def is_registered(self, device_id: str) -> bool:
        return device_id in self.by_device

    def list_registrations(self, department: str = None) -> List[DeviceRegistration]:
        regs = list(self.registrations.values())
        if department:
            regs = [r for r in regs if r.department == department]
        return regs

    def count(self) -> int:
        return len(self.registrations)
