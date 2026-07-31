"""
Integration Config - Configuration management
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ConfigFormat(Enum):
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    TOML = "toml"


@dataclass
class ConfigEntry:
    key: str
    value: Any
    category: str = "general"
    encrypted: bool = False
    description: str = ""
    updated_at: datetime = field(default_factory=datetime.now)


class IntegrationConfig:
    def __init__(self):
        self.entries: dict[str, ConfigEntry] = {}
        self.namespaces: dict[str, dict[str, Any]] = {}
        self.defaults: dict[str, Any] = {"timeout": 30, "retries": 3, "batch_size": 100, "log_level": "info"}
        self.environments: dict[str, dict[str, Any]] = {}

    def set(
        self, key: str, value: Any, category: str = "general", encrypted: bool = False, description: str = ""
    ) -> ConfigEntry:
        entry = ConfigEntry(key=key, value=value, category=category, encrypted=encrypted, description=description)
        self.entries[key] = entry
        return entry

    def get(self, key: str, default: Any = None) -> Any:
        entry = self.entries.get(key)
        return entry.value if entry else self.defaults.get(key, default)

    def delete(self, key: str) -> bool:
        if key in self.entries:
            del self.entries[key]
            return True
        return False

    def get_namespace(self, namespace: str) -> dict[str, Any]:
        return self.namespaces.get(namespace, {})

    def set_namespace(self, namespace: str, values: dict[str, Any]) -> None:
        self.namespaces[namespace] = values

    def set_default(self, key: str, value: Any) -> None:
        self.defaults[key] = value

    def get_all(self, category: str = None) -> dict[str, Any]:
        if category:
            return {k: v.value for k, v in self.entries.items() if v.category == category}
        return {k: v.value for k, v in self.entries.items()}

    def define_environment(self, name: str, config: dict[str, Any]) -> None:
        self.environments[name] = config

    def get_environment(self, name: str) -> dict[str, Any]:
        return self.environments.get(name, {})

    def list_categories(self) -> list[str]:
        return list(set(e.category for e in self.entries.values()))

    def count(self) -> int:
        return len(self.entries)
