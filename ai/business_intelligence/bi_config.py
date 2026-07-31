"""BI Config — Configuration management for BI operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ConfigEntry:
    key: str
    value: Any
    section: str = "general"
    description: str = ""
    updated_at: datetime = field(default_factory=datetime.now)


class BIConfig:
    def __init__(self):
        self.entries: dict[str, ConfigEntry] = {}
        self.defaults: dict[str, Any] = {
            "refresh_interval": 300,
            "max_data_points": 100000,
            "prediction_horizon": 90,
            "confidence_threshold": 0.7,
            "dashboard_refresh": 60,
            "report_schedule": "daily",
        }

    def set(self, key: str, value: Any, section: str = "general", description: str = "") -> ConfigEntry:
        entry = ConfigEntry(key=key, value=value, section=section, description=description)
        self.entries[key] = entry
        return entry

    def get(self, key: str, default: Any = None) -> Any:
        entry = self.entries.get(key)
        if entry:
            return entry.value
        return self.defaults.get(key, default)

    def get_section(self, section: str) -> dict[str, Any]:
        return {k: v.value for k, v in self.entries.items() if v.section == section}

    def get_all(self) -> dict[str, Any]:
        result = dict(self.defaults)
        result.update({k: v.value for k, v in self.entries.items()})
        return result

    def delete(self, key: str) -> bool:
        if key in self.entries:
            del self.entries[key]
            return True
        return False

    def count(self) -> int:
        return len(self.entries)
