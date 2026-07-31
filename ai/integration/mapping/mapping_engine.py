"""
Mapping Engine - Core data mapping
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MappingRule:
    rule_id: str
    source_field: str
    target_field: str
    transform: str = ""
    default_value: Any = None
    required: bool = False


@dataclass
class MappingConfig:
    name: str
    source_schema: str
    target_schema: str
    rules: list[MappingRule] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class MappingEngine:
    def __init__(self):
        self.mappings: dict[str, MappingConfig] = {}
        self.transform_log: list[dict[str, Any]] = []

    def create_mapping(self, name: str, source_schema: str, target_schema: str) -> MappingConfig:
        config = MappingConfig(name=name, source_schema=source_schema, target_schema=target_schema)
        self.mappings[name] = config
        return config

    def add_rule(self, mapping_name: str, source_field: str, target_field: str, transform: str = "", default_value: Any = None) -> MappingRule:
        config = self.mappings.get(mapping_name)
        if config:
            rule = MappingRule(rule_id=hashlib.sha256(f"{source_field}{target_field}".encode()).hexdigest()[:16], source_field=source_field, target_field=target_field, transform=transform, default_value=default_value)
            config.rules.append(rule)
            return rule
        return None

    def map_data(self, mapping_name: str, source_data: dict[str, Any]) -> dict[str, Any]:
        config = self.mappings.get(mapping_name)
        if not config:
            return source_data
        result = {}
        for rule in config.rules:
            value = source_data.get(rule.source_field, rule.default_value)
            if rule.transform:
                value = self._apply_transform(value, rule.transform)
            result[rule.target_field] = value
        self.transform_log.append({"mapping": mapping_name, "timestamp": datetime.now().isoformat(), "fields_mapped": len(result)})
        return result

    def _apply_transform(self, value: Any, transform: str) -> Any:
        if transform == "upper" and isinstance(value, str):
            return value.upper()
        elif transform == "lower" and isinstance(value, str):
            return value.lower()
        elif transform == "str":
            return str(value)
        elif transform == "int":
            return int(value) if value else 0
        elif transform == "float":
            return float(value) if value else 0.0
        return value

    def get_mapping(self, name: str) -> MappingConfig | None:
        return self.mappings.get(name)

    def list_mappings(self) -> list[MappingConfig]:
        return list(self.mappings.values())

    def count(self) -> int:
        return len(self.mappings)
