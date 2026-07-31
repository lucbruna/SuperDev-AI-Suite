"""
Adapter Engine - Core adaptation logic
"""

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AdapterType(Enum):
    PROTOCOL = "protocol"
    FORMAT = "format"
    DATA = "data"
    API = "api"
    LEGACY = "legacy"
    CUSTOM = "custom"


@dataclass
class AdapterConfig:
    name: str
    adapter_type: AdapterType
    source_format: str = ""
    target_format: str = ""
    rules: dict[str, str] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class TranslationResult:
    success: bool
    data: Any = None
    error: str = ""
    adapter_name: str = ""


class AdapterEngine:
    def __init__(self):
        self.adapters: dict[str, AdapterConfig] = {}
        self.handlers: dict[str, Callable] = {}
        self.translation_log: list[TranslationResult] = []

    def register_adapter(self, config: AdapterConfig) -> str:
        adapter_id = hashlib.sha256(f"{config.name}{config.adapter_type.value}".encode()).hexdigest()[:16]
        self.adapters[adapter_id] = config
        return adapter_id

    def register_handler(self, adapter_id: str, handler: Callable) -> None:
        self.handlers[adapter_id] = handler

    def translate(self, adapter_id: str, data: Any) -> TranslationResult:
        adapter = self.adapters.get(adapter_id)
        if not adapter:
            result = TranslationResult(success=False, error="Adapter not found")
            self.translation_log.append(result)
            return result
        handler = self.handlers.get(adapter_id)
        if handler:
            try:
                translated = handler(data, adapter.rules)
                result = TranslationResult(success=True, data=translated, adapter_name=adapter.name)
            except Exception as e:
                result = TranslationResult(success=False, error=str(e), adapter_name=adapter.name)
        else:
            result = TranslationResult(success=True, data=data, adapter_name=adapter.name)
        self.translation_log.append(result)
        return result

    def get_adapter(self, adapter_id: str) -> AdapterConfig | None:
        return self.adapters.get(adapter_id)

    def list_adapters(self) -> list[AdapterConfig]:
        return list(self.adapters.values())

    def get_log(self, limit: int = 100) -> list[TranslationResult]:
        return self.translation_log[-limit:]

    def count(self) -> int:
        return len(self.adapters)
