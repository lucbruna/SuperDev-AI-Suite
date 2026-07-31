"""Mobile Platform & Edge AI Engine - Core engine for mobile and edge computing."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class PlatformType(Enum):
    ANDROID = "android"
    IOS = "ios"
    TABLET = "tablet"
    WEARABLE = "wearable"
    EDGE_DEVICE = "edge_device"


class MobileState(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"
    ERROR = "error"
    LOW_BATTERY = "low_battery"


@dataclass
class MobileDevice:
    device_id: str
    name: str
    platform: PlatformType
    os_version: str = ""
    state: MobileState = MobileState.ONLINE
    last_sync: Optional[datetime] = None
    battery_level: float = 100.0
    storage_used_mb: float = 0.0
    ai_models_loaded: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MobileEngine:
    def __init__(self):
        self.devices: Dict[str, MobileDevice] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.event_log: List[Dict[str, Any]] = []

    def register_device(self, name: str, platform: PlatformType, os_version: str = "") -> MobileDevice:
        device_id = hashlib.sha256(f"{name}{platform.value}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        device = MobileDevice(device_id=device_id, name=name, platform=platform, os_version=os_version)
        self.devices[device_id] = device
        self._log_event("device_registered", device_id)
        return device

    def get_device(self, device_id: str) -> Optional[MobileDevice]:
        return self.devices.get(device_id)

    def update_state(self, device_id: str, state: MobileState) -> bool:
        device = self.devices.get(device_id)
        if device:
            device.state = state
            self._log_event("state_changed", device_id, {"state": state.value})
            return True
        return False

    def list_devices(self, platform: PlatformType = None) -> List[MobileDevice]:
        if platform:
            return [d for d in self.devices.values() if d.platform == platform]
        return list(self.devices.values())

    def get_online_devices(self) -> List[MobileDevice]:
        return [d for d in self.devices.values() if d.state == MobileState.ONLINE]

    def start_session(self, device_id: str, session_data: Dict[str, Any] = None) -> Optional[str]:
        device = self.devices.get(device_id)
        if not device:
            return None
        session_id = hashlib.sha256(f"{device_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        self.active_sessions[session_id] = {"device_id": device_id, "started_at": datetime.now().isoformat(), "data": session_data or {}}
        self._log_event("session_started", device_id, {"session_id": session_id})
        return session_id

    def end_session(self, session_id: str) -> bool:
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False

    def count(self) -> int:
        return len(self.devices)

    def _log_event(self, event_type: str, device_id: str, data: Dict[str, Any] = None):
        self.event_log.append({"event_type": event_type, "device_id": device_id, "data": data or {}, "timestamp": datetime.now().isoformat()})
