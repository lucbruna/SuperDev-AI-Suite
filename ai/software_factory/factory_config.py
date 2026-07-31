"""Factory Config - Configuration management for factory operations."""
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


class FactoryConfig:
    def __init__(self):
        self.entries: dict[str, ConfigEntry] = {}
        self.defaults: dict[str, Any] = {}

    def set(self, key: str, value: Any, section: str = "general", description: str = "") -> ConfigEntry:
        entry = ConfigEntry(key=key, value=value, section=section, description=description)
        self.entries[key] = entry
        return entry

    def get(self, key: str, default: Any = None) -> Any:
        entry = self.entries.get(key)
        if entry:
            return entry.value
        return self.defaults.get(key, default)

    def delete(self, key: str) -> bool:
        if key in self.entries:
            del self.entries[key]
            return True
        return False

    def set_default(self, key: str, value: Any) -> None:
        self.defaults[key] = value

    def list_entries(self, section: str = None) -> list[ConfigEntry]:
        entries = list(self.entries.values())
        if section:
            entries = [e for e in entries if e.section == section]
        return entries

    def count(self) -> int:
        return len(self.entries)
