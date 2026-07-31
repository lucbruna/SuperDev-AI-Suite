"""Mobile Configuration - Platform and device configuration management."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ConfigScope(Enum):
    GLOBAL = "global"
    PLATFORM = "platform"
    DEVICE = "device"
    USER = "user"


@dataclass
class MobileConfigEntry:
    key: str
    value: Any
    scope: ConfigScope = ConfigScope.GLOBAL
    platform: str = ""
    device_id: str = ""
    user_id: str = ""
    default: Any = None
    description: str = ""
    updated_at: datetime = field(default_factory=datetime.now)


class MobileConfig:
    def __init__(self):
        self.entries: Dict[str, MobileConfigEntry] = {}
        self.overrides: Dict[str, Dict[str, Any]] = {}
        self.history: List[Dict[str, Any]] = []

    def set(self, key: str, value: Any, scope: ConfigScope = ConfigScope.GLOBAL, **kwargs) -> MobileConfigEntry:
        entry = MobileConfigEntry(key=key, value=value, scope=scope, **kwargs)
        self.entries[key] = entry
        self.history.append({"action": "set", "key": key, "value": value, "timestamp": datetime.now().isoformat()})
        return entry

    def get(self, key: str, device_id: str = "", platform: str = "") -> Any:
        entry = self.entries.get(key)
        if not entry:
            return None
        if device_id and device_id in self.overrides.get(key, {}):
            return self.overrides[key][device_id]
        if platform and entry.platform == platform:
            return entry.value
        if entry.scope == ConfigScope.GLOBAL:
            return entry.value
        return entry.default

    def delete(self, key: str) -> bool:
        if key in self.entries:
            del self.entries[key]
            self.history.append({"action": "delete", "key": key, "timestamp": datetime.now().isoformat()})
            return True
        return False

    def set_override(self, key: str, device_id: str, value: Any) -> None:
        self.overrides.setdefault(key, {})[device_id] = value

    def list_entries(self, scope: ConfigScope = None) -> List[MobileConfigEntry]:
        entries = list(self.entries.values())
        if scope:
            entries = [e for e in entries if e.scope == scope]
        return entries

    def get_all(self, platform: str = "", device_id: str = "") -> Dict[str, Any]:
        result = {}
        for key, entry in self.entries.items():
            if platform and entry.platform and entry.platform != platform:
                continue
            result[key] = self.get(key, device_id=device_id, platform=platform)
        return result

    def count(self) -> int:
        return len(self.entries)
