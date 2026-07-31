"""
Legacy Adapter - Legacy system integration
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class LegacySystemType(Enum):
    MAINFRAME = "mainframe"
    AS400 = "as400"
    DOS = "dos"
    COBOL = "cobol"
    VT100 = "vt100"
    CUSTOM = "custom"


@dataclass
class LegacyConfig:
    system_type: LegacySystemType
    connection_string: str = ""
    encoding: str = "utf-8"
    delimiter: str = ","
    line_ending: str = "\n"
    settings: Dict[str, Any] = field(default_factory=dict)


class LegacyAdapter:
    def __init__(self):
        self.configs: Dict[str, LegacyConfig] = {}
        self.transformations: Dict[str, List[Dict[str, str]]] = {}

    def register_system(self, name: str, system_type: LegacySystemType, **kwargs) -> LegacyConfig:
        config = LegacyConfig(system_type=system_type, **kwargs)
        self.configs[name] = config
        return config

    def add_transformation(self, system_name: str, field_mapping: Dict[str, str]) -> None:
        self.transformations.setdefault(system_name, []).append(field_mapping)

    def transform_data(self, system_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        mappings = self.transformations.get(system_name, [])
        result = dict(data)
        for mapping in mappings:
            for old_key, new_key in mapping.items():
                if old_key in result:
                    result[new_key] = result.pop(old_key)
        return result

    def get_config(self, system_name: str) -> Optional[LegacyConfig]:
        return self.configs.get(system_name)

    def list_systems(self) -> List[str]:
        return list(self.configs.keys())

    def count(self) -> int:
        return len(self.configs)
