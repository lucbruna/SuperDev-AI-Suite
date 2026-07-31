from __future__ import annotations

import itertools
import logging
from typing import Any

from .integration_config import IntegrationConfig
from .integration_events import IntegrationEvents, IntegrationEventType
from .integration_metrics import IntegrationMetrics
from .integration_models import (
    APIEndpoint,
    ConnectionConfig,
    ConnectionRecord,
    ConnectorStatus,
)
from .integration_registry import IntegrationRegistry
from .integration_security import IntegrationSecurity


class IntegrationManager:
    """High-level orchestration of connections, API endpoints, and integrations."""

    def __init__(
        self,
        config: IntegrationConfig | None = None,
        registry: IntegrationRegistry | None = None,
        events: IntegrationEvents | None = None,
        metrics: IntegrationMetrics | None = None,
        security: IntegrationSecurity | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.integration.manager")
        self.config = config or IntegrationConfig()
        self.registry = registry or IntegrationRegistry()
        self.events = events or IntegrationEvents()
        self.metrics = metrics or IntegrationMetrics()
        self.security = security or IntegrationSecurity(self.config.enable_auth)
        self._connections: dict[str, ConnectionRecord] = {}
        self._connector_instances: dict[str, Any] = {}
        self._endpoints: dict[str, APIEndpoint] = {}
        self._ids = itertools.count(1)

    # --- Connections ---------------------------------------------------------

    def create_connection(self, config: ConnectionConfig) -> str:
        connection_id = f"conn-{next(self._ids)}"
        self._connections[connection_id] = ConnectionRecord(
            connection_id=connection_id, config=config
        )
        self.metrics.increment("connections.created")
        self.events.emit(
            IntegrationEventType.CONNECTION_CREATED,
            {"connection_id": connection_id, "type": config.connector_type},
        )
        return connection_id

    def get_connection(self, connection_id: str) -> ConnectionRecord | None:
        return self._connections.get(connection_id)

    def list_connections(self) -> list[ConnectionRecord]:
        return list(self._connections.values())

    def remove_connection(self, connection_id: str) -> bool:
        record = self._connections.pop(connection_id, None)
        if record is None:
            return False
        self._connector_instances.pop(connection_id, None)
        return True

    def connect(self, connection_id: str) -> bool:
        record = self._connections.get(connection_id)
        if record is None:
            raise KeyError(f"unknown connection {connection_id!r}")
        connector = self._get_connector(connection_id, record)
        with self.metrics.time("connection.connect"):
            connected = connector.connect(record.config)
        record.status = ConnectorStatus.CONNECTED if connected else ConnectorStatus.ERROR
        record.error = "" if connected else "connector refused connection"
        record.connected_at = "" if not connected else record.updated_at
        self.events.emit(
            IntegrationEventType.CONNECTION_CONNECTED
            if connected
            else IntegrationEventType.CONNECTION_ERROR,
            {"connection_id": connection_id},
        )
        return connected

    def disconnect(self, connection_id: str) -> bool:
        connector = self._connector_instances.get(connection_id)
        if connector is None:
            record = self._connections.get(connection_id)
            if record is not None:
                record.status = ConnectorStatus.DISCONNECTED
            return True
        ok = connector.disconnect()
        record = self._connections.get(connection_id)
        if record is not None:
            record.status = ConnectorStatus.DISCONNECTED if ok else record.status
        self.events.emit(
            IntegrationEventType.CONNECTION_DISCONNECTED, {"connection_id": connection_id}
        )
        return ok

    def invoke(self, connection_id: str, operation: str,
               params: dict[str, Any] | None = None) -> Any:
        record = self._connections.get(connection_id)
        if record is None:
            raise KeyError(f"unknown connection {connection_id!r}")
        connector = self._connector_instances.get(connection_id)
        if connector is None:
            raise RuntimeError(f"connection {connection_id!r} is not connected")
        if not connector.is_connected():
            raise RuntimeError(f"connection {connection_id!r} is not connected")
        with self.metrics.time("connection.invoke"):
            result = connector.invoke(operation, params or {})
        self.metrics.increment("connections.invokes")
        return result

    def test_connection(self, connection_id: str) -> bool:
        record = self._connections.get(connection_id)
        if record is None:
            raise KeyError(f"unknown connection {connection_id!r}")
        connector = self._get_connector(connection_id, record)
        return connector.test()

    def _get_connector(self, connection_id: str, record: ConnectionRecord) -> Any:
        if connection_id not in self._connector_instances:
            self._connector_instances[connection_id] = self._build_connector(record.config)
        return self._connector_instances[connection_id]

    def _build_connector(self, config: ConnectionConfig) -> Any:
        from .integration_factory import IntegrationFactory

        factory = IntegrationFactory(self.config, self.registry)
        return factory.build_connector(config.connector_type)

    # --- API endpoints ---------------------------------------------------------

    def register_endpoint(self, endpoint: APIEndpoint) -> str:
        key = f"{endpoint.method.upper()} {endpoint.path}"
        self._endpoints[key] = endpoint
        self.metrics.increment("api.endpoints")
        self.events.emit(IntegrationEventType.API_REGISTERED, {"endpoint": key})
        return key

    def list_endpoints(self) -> list[APIEndpoint]:
        return list(self._endpoints.values())

    def get_endpoint(self, method: str, path: str) -> APIEndpoint | None:
        return self._endpoints.get(f"{method.upper()} {path}")

    def route(self, method: str, path: str, connection_id: str,
              operation: str, params: dict[str, Any] | None = None) -> Any:
        """Routes a gateway request to a connection operation."""
        endpoint = self.get_endpoint(method, path)
        if endpoint is None:
            raise KeyError(f"no endpoint for {method.upper()} {path}")
        return self.invoke(connection_id, endpoint.operation, params)

    # --- Lifecycle ---------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "connections": len(self._connections),
            "connected": sum(
                1 for c in self._connections.values() if c.status == ConnectorStatus.CONNECTED
            ),
            "endpoints": len(self._endpoints),
            "metrics": self.metrics.snapshot(),
            "registry": self.registry.snapshot(),
        }

    def shutdown(self) -> None:
        for connection_id in list(self._connector_instances):
            self.disconnect(connection_id)
