"""
Protocol Adapter - Protocol translation
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Protocol(Enum):
    REST = "rest"
    SOAP = "soap"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    MQTT = "mqtt"


@dataclass
class ProtocolTranslation:
    source_protocol: Protocol
    target_protocol: Protocol
    rules: dict[str, Any] = field(default_factory=dict)


class ProtocolAdapter:
    def __init__(self):
        self.translations: dict[str, ProtocolTranslation] = {}
        self.supported_pairs: list[tuple] = []

    def register_translation(self, source: Protocol, target: Protocol, rules: dict[str, Any] = None) -> ProtocolTranslation:
        key = f"{source.value}:{target.value}"
        translation = ProtocolTranslation(source_protocol=source, target_protocol=target, rules=rules or {})
        self.translations[key] = translation
        self.supported_pairs.append((source, target))
        return translation

    def translate(self, data: Any, source: Protocol, target: Protocol) -> Any:
        key = f"{source.value}:{target.value}"
        translation = self.translations.get(key)
        if translation:
            return {"data": data, "source": source.value, "target": target.value, "applied_rules": translation.rules}
        return data

    def is_supported(self, source: Protocol, target: Protocol) -> bool:
        return (source, target) in self.supported_pairs

    def get_translation(self, source: Protocol, target: Protocol) -> ProtocolTranslation | None:
        return self.translations.get(f"{source.value}:{target.value}")

    def list_translations(self) -> list[ProtocolTranslation]:
        return list(self.translations.values())

    def count(self) -> int:
        return len(self.translations)
