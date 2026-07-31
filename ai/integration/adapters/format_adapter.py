"""
Format Adapter - Data format translation
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DataFormat(Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    PROTOBUF = "protobuf"


@dataclass
class FormatRule:
    source_field: str
    target_field: str
    transform: str = ""
    default_value: Any = None


class FormatAdapter:
    def __init__(self):
        self.formats: dict[str, DataFormat] = {}
        self.rules: dict[str, list[FormatRule]] = {}

    def register_format(self, name: str, format_type: DataFormat) -> None:
        self.formats[name] = format_type

    def add_rule(self, source_format: str, target_format: str, rule: FormatRule) -> None:
        key = f"{source_format}:{target_format}"
        self.rules.setdefault(key, []).append(rule)

    def translate(self, data: dict[str, Any], source_format: str, target_format: str) -> dict[str, Any]:
        key = f"{source_format}:{target_format}"
        rules = self.rules.get(key, [])
        result = {}
        for rule in rules:
            value = data.get(rule.source_field, rule.default_value)
            result[rule.target_field] = value
        return result

    def get_rules(self, source_format: str, target_format: str) -> list[FormatRule]:
        return self.rules.get(f"{source_format}:{target_format}", [])

    def list_formats(self) -> list[str]:
        return list(self.formats.keys())

    def count(self) -> int:
        return len(self.formats)
