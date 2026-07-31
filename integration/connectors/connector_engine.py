from __future__ import annotations

import logging
from typing import Any

from ..integration_models import ConnectionConfig, ConnectionRecord
from .connector_health import ConnectorHealth
from .connector_manager import ConnectorManager
from .connector_registry import ConnectorRegistry
from .connector_validator import ConnectorValidator


class ConnectorEngine:
    """Facade for the connectors subsystem: registry, validation, lifecycle, health."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.connectors")
        self.registry = ConnectorRegistry()
        self.validator = ConnectorValidator()
        self.health = ConnectorHealth()
        self.manager = ConnectorManager(self.registry, self.validator, self.health)

    def register(self, connector_type: str, connector_class: type) -> None:
        self.registry.register(connector_type, connector_class)

    def connect(self, config: ConnectionConfig) -> bool:
        return self.manager.connect(config)

    def disconnect(self, config: ConnectionConfig) -> bool:
        return self.manager.disconnect(config)

    def invoke(self, config: ConnectionConfig, operation: str,
               params: dict[str, Any] | None = None) -> Any:
        return self.manager.invoke(config, operation, params)

    def validate(self, config: ConnectionConfig) -> list[str]:
        return self.validator.validate(config)

    def check(self, connection_id: str, config: ConnectionConfig) -> Any:
        return self.manager.health_report(connection_id, config)

    def list_types(self) -> list[str]:
        return self.registry.list()

    def stats(self) -> dict[str, int]:
        return self.manager.snapshot()
