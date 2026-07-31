"""
Integration Interfaces - Abstract interfaces
"""
from dataclasses import dataclass, field
from typing import Any, Protocol


class ConnectorInterface(Protocol):
    def connect(self) -> bool: ...
    def disconnect(self) -> bool: ...
    def is_connected(self) -> bool: ...
    def send(self, data: Any) -> Any: ...
    def receive(self) -> Any: ...


class AdapterInterface(Protocol):
    def translate(self, data: Any, source_format: str, target_format: str) -> Any: ...
    def validate(self, data: Any) -> bool: ...


class MapperInterface(Protocol):
    def map(self, source: Any, mapping_rules: dict[str, str]) -> Any: ...
    def validate_mapping(self, source_schema: dict, target_schema: dict) -> bool: ...


class SyncInterface(Protocol):
    def sync(self, source: Any, target: Any) -> bool: ...
    def get_conflicts(self) -> list[dict]: ...
    def resolve_conflict(self, conflict_id: str, resolution: Any) -> bool: ...


class QueueInterface(Protocol):
    def enqueue(self, item: Any) -> str: ...
    def dequeue(self) -> Any | None: ...
    def size(self) -> int: ...
    def is_empty(self) -> bool: ...


class MonitorInterface(Protocol):
    def health_check(self) -> dict[str, Any]: ...
    def get_metrics(self) -> dict[str, Any]: ...
    def get_status(self) -> str: ...


@dataclass
class IntegrationCapabilities:
    supports_batch: bool = False
    supports_streaming: bool = False
    supports_pagination: bool = False
    supports_filtering: bool = False
    supports_sorting: bool = False
    max_batch_size: int = 100
    rate_limit: int = 1000
    data_formats: list[str] = field(default_factory=lambda: ["json"])


class IntegrationInterfaces:
    def __init__(self):
        self.capabilities: dict[str, IntegrationCapabilities] = {}
        self.interface_registry: dict[str, str] = {}

    def register_capabilities(self, integration_id: str, capabilities: IntegrationCapabilities) -> None:
        self.capabilities[integration_id] = capabilities

    def get_capabilities(self, integration_id: str) -> IntegrationCapabilities | None:
        return self.capabilities.get(integration_id)

    def register_interface(self, integration_id: str, interface_type: str) -> None:
        self.interface_registry[integration_id] = interface_type

    def get_interface_type(self, integration_id: str) -> str | None:
        return self.interface_registry.get(integration_id)

    def has_capability(self, integration_id: str, capability: str) -> bool:
        caps = self.capabilities.get(integration_id)
        return getattr(caps, capability, False) if caps else False

    def count(self) -> int:
        return len(self.capabilities)
