"""
Integration Config - Configuration management
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


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
        self.entries: Dict[str, ConfigEntry] = {}
        self.namespaces: Dict[str, Dict[str, Any]] = {}
        self.defaults: Dict[str, Any] = {"timeout": 30, "retries": 3, "batch_size": 100, "log_level": "info"}
        self.environments: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, value: Any, category: str = "general", encrypted: bool = False, description: str = "") -> ConfigEntry:
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

    def get_namespace(self, namespace: str) -> Dict[str, Any]:
        return self.namespaces.get(namespace, {})

    def set_namespace(self, namespace: str, values: Dict[str, Any]) -> None:
        self.namespaces[namespace] = values

    def set_default(self, key: str, value: Any) -> None:
        self.defaults[key] = value

    def get_all(self, category: str = None) -> Dict[str, Any]:
        if category:
            return {k: v.value for k, v in self.entries.items() if v.category == category}
        return {k: v.value for k, v in self.entries.items()}

    def define_environment(self, name: str, config: Dict[str, Any]) -> None:
        self.environments[name] = config

    def get_environment(self, name: str) -> Dict[str, Any]:
        return self.environments.get(name, {})

    def list_categories(self) -> List[str]:
        return list(set(e.category for e in self.entries.values()))

    def count(self) -> int:
        return len(self.entries)
