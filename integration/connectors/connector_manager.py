from __future__ import annotations

import logging
from typing import Any

from ..integration_models import ConnectionConfig, ConnectionRecord, ConnectorStatus
from .connector_health import ConnectorHealth
from .connector_registry import ConnectorRegistry
from .connector_validator import ConnectorValidator


class ConnectorManager:
    """Manages connector instances for connections: create, connect, invoke."""

    def __init__(
        self,
        registry: ConnectorRegistry | None = None,
        validator: ConnectorValidator | None = None,
        health: ConnectorHealth | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.integration.connectors.manager")
        self.registry = registry or ConnectorRegistry()
        self.validator = validator or ConnectorValidator()
        self.health = health or ConnectorHealth()
        self._instances: dict[str, Any] = {}

    def build(self, config: ConnectionConfig) -> Any:
        """Builds (or reuses) a connector instance for a config."""
        key = f"{config.name}:{config.connector_type}"
        if key not in self._instances:
            connector = self.registry.create(config.connector_type)
            if connector is None:
                from .connector_template import GenericConnector

                connector = GenericConnector(config.connector_type)
            self._instances[key] = connector
        return self._instances[key]

    def connect(self, config: ConnectionConfig) -> bool:
        errors = self.validator.validate(config)
        if errors:
            raise ValueError(f"invalid connector config: {errors}")
        connector = self.build(config)
        return connector.connect(config)

    def disconnect(self, config: ConnectionConfig) -> bool:
        key = f"{config.name}:{config.connector_type}"
        connector = self._instances.get(key)
        if connector is None:
            return True
        return connector.disconnect()

    def invoke(self, config: ConnectionConfig, operation: str,
               params: dict[str, Any] | None = None) -> Any:
        connector = self.build(config)
        if not connector.is_connected():
            raise RuntimeError(f"connector {config.connector_type!r} is not connected")
        return connector.invoke(operation, params or {})

    def health_report(self, connection_id: str, config: ConnectionConfig) -> Any:
        connector = self.build(config)
        return self.health.check_connector(connection_id, connector)

    def status(self, config: ConnectionConfig) -> str:
        connector = self.build(config)
        return connector.status()

    def snapshot(self) -> dict[str, int]:
        return {
            "instances": len(self._instances),
            "connector_types": len(self.registry.list()),
            "schemas": self.validator.snapshot()["schemas"],
            "health": self.health.snapshot()["total"],
        }
