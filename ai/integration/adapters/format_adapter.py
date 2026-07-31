"""
Format Adapter - Data format translation
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


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
        self.formats: Dict[str, DataFormat] = {}
        self.rules: Dict[str, List[FormatRule]] = {}

    def register_format(self, name: str, format_type: DataFormat) -> None:
        self.formats[name] = format_type

    def add_rule(self, source_format: str, target_format: str, rule: FormatRule) -> None:
        key = f"{source_format}:{target_format}"
        self.rules.setdefault(key, []).append(rule)

    def translate(self, data: Dict[str, Any], source_format: str, target_format: str) -> Dict[str, Any]:
        key = f"{source_format}:{target_format}"
        rules = self.rules.get(key, [])
        result = {}
        for rule in rules:
            value = data.get(rule.source_field, rule.default_value)
            result[rule.target_field] = value
        return result

    def get_rules(self, source_format: str, target_format: str) -> List[FormatRule]:
        return self.rules.get(f"{source_format}:{target_format}", [])

    def list_formats(self) -> List[str]:
        return list(self.formats.keys())

    def count(self) -> int:
        return len(self.formats)
