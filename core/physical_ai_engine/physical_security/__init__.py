from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from .access_control import AccessControl
from .device_authentication import DeviceAuthentication
from .safety_manager import SafetyManager
from .emergency_control import EmergencyControl

logger = logging.getLogger(__name__)


PHYSICAL_ROLES: Dict[str, Set[str]] = {
    "plant_manager": {"read", "write", "configure", "approve", "emergency_stop", "audit", "override"},
    "engineer": {"read", "write", "configure", "calibrate", "emergency_stop"},
    "operator": {"read", "write", "start", "stop", "emergency_stop"},
    "technician": {"read", "write", "maintain", "calibrate"},
    "inspector": {"read", "inspect", "audit"},
    "viewer": {"read"},
}


class PhysicalSecurityManager:
    def __init__(self, config=None):
        from ..physical_config import PhysicalConfig
        self._config = config or PhysicalConfig()
        self._access = AccessControl(self._config)
        self._device_auth = DeviceAuthentication(self._config)
        self._safety = SafetyManager(self._config)
        self._emergency = EmergencyControl(self._config)
        self._roles: Dict[str, str] = {}

    @property
    def access(self) -> AccessControl:
        return self._access

    @property
    def device_auth(self) -> DeviceAuthentication:
        return self._device_auth

    @property
    def safety(self) -> SafetyManager:
        return self._safety

    @property
    def emergency(self) -> EmergencyControl:
        return self._emergency

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        role = self._roles.get(user_id)
        if not role:
            return False
        return action in PHYSICAL_ROLES.get(role, set())

    def set_user_role(self, user_id: str, role: str) -> None:
        if role not in PHYSICAL_ROLES:
            raise ValueError(f"Invalid physical role: {role}")
        self._roles[user_id] = role

    def authenticate_device(self, device_id: str, token: str) -> bool:
        return self._device_auth.authenticate(device_id, token)

    def register_device_credentials(self, device_id: str, secret: str) -> None:
        self._device_auth.register(device_id, secret)

    def check_safety_zone(self, robot_id: str, position: Dict[str, float]) -> bool:
        return self._safety.check_zone(robot_id, position)

    def trigger_emergency_stop(self, source: str, reason: str) -> Dict[str, Any]:
        return self._emergency.trigger(source, reason)

    def reset_emergency_stop(self) -> bool:
        return self._emergency.reset()

    def is_emergency_active(self) -> bool:
        return self._emergency.is_active()

    def get_security_report(self) -> Dict[str, Any]:
        return {
            "access_control": True,
            "device_authentication": True,
            "safety_monitoring": True,
            "emergency_stop": True,
            "roles": list(PHYSICAL_ROLES.keys()),
        }


__all__ = [
    "PhysicalSecurityManager",
    "AccessControl",
    "DeviceAuthentication",
    "SafetyManager",
    "EmergencyControl",
]
