from __future__ import annotations

import logging
from typing import Any

from .integration_config import IntegrationConfig
from .integration_context import IntegrationContext, IntegrationResult
from .integration_events import IntegrationEventType, IntegrationEvents
from .integration_manager import IntegrationManager
from .integration_metrics import IntegrationMetrics
from .integration_models import APIEndpoint, ConnectionConfig, IntegrationDefinition
from .integration_registry import IntegrationRegistry
from .integration_runtime import IntegrationRuntime
from .integration_security import IntegrationSecurity


class IntegrationEngine:
    """Top-level facade for the Integration & API Engine."""

    def __init__(
        self,
        config: IntegrationConfig | None = None,
        runtime: IntegrationRuntime | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.integration.engine")
        self.config = config or IntegrationConfig()
        self.runtime = runtime or IntegrationRuntime(self.config)
        self.events: IntegrationEvents = self.runtime.events
        self.metrics: IntegrationMetrics = self.runtime.metrics
        self.registry: IntegrationRegistry = self.runtime.registry
        self.security: IntegrationSecurity = self.runtime.security

    def initialize(self) -> "IntegrationEngine":
        self.runtime.start()
        return self

    @property
    def manager(self) -> IntegrationManager | None:
        return self.runtime.manager

    # --- Connections ---------------------------------------------------------

    def create_connection(self, config: ConnectionConfig) -> IntegrationResult:
        try:
            if self.manager is None:
                return IntegrationResult.fail("create_connection", "engine not initialized")
            connection_id = self.manager.create_connection(config)
            return IntegrationResult.ok("create_connection", {"connection_id": connection_id})
        except Exception as exc:  # noqa: BLE001
            return IntegrationResult.fail("create_connection", str(exc))

    def connect(self, connection_id: str) -> IntegrationResult:
        try:
            if self.manager is None:
                return IntegrationResult.fail("connect", "engine not initialized")
            connected = self.manager.connect(connection_id)
            return IntegrationResult.ok("connect", {"connection_id": connection_id,
                                                    "connected": connected})
        except Exception as exc:  # noqa: BLE001
            return IntegrationResult.fail("connect", str(exc))

    def disconnect(self, connection_id: str) -> IntegrationResult:
        try:
            if self.manager is None:
                return IntegrationResult.fail("disconnect", "engine not initialized")
            self.manager.disconnect(connection_id)
            return IntegrationResult.ok("disconnect", {"connection_id": connection_id})
        except Exception as exc:  # noqa: BLE001
            return IntegrationResult.fail("disconnect", str(exc))

    def invoke(self, connection_id: str, operation: str,
               params: dict[str, Any] | None = None,
               context: IntegrationContext | None = None) -> IntegrationResult:
        try:
            if self.manager is None:
                return IntegrationResult.fail("invoke", "engine not initialized")
            result = self.manager.invoke(connection_id, operation, params)
            return IntegrationResult.ok("invoke", result)
        except Exception as exc:  # noqa: BLE001
            return IntegrationResult.fail("invoke", str(exc))

    def list_connections(self) -> IntegrationResult:
        try:
            if self.manager is None:
                return IntegrationResult.fail("list_connections", "engine not initialized")
            connections = [c.to_dict() for c in self.manager.list_connections()]
            return IntegrationResult.ok("list_connections", connections)
        except Exception as exc:  # noqa: BLE001
            return IntegrationResult.fail("list_connections", str(exc))

    # --- API -----------------------------------------------------------------

    def register_endpoint(self, endpoint: APIEndpoint) -> IntegrationResult:
        try:
            if self.manager is None:
                return IntegrationResult.fail("register_endpoint", "engine not initialized")
            key = self.manager.register_endpoint(endpoint)
            return IntegrationResult.ok("register_endpoint", {"endpoint": key})
        except Exception as exc:  # noqa: BLE001
            return IntegrationResult.fail("register_endpoint", str(exc))

    def route(self, method: str, path: str, connection_id: str,
              operation: str, params: dict[str, Any] | None = None) -> IntegrationResult:
        try:
            if self.manager is None:
                return IntegrationResult.fail("route", "engine not initialized")
            data = self.manager.route(method, path, connection_id, operation, params)
            return IntegrationResult.ok("route", data)
        except Exception as exc:  # noqa: BLE001
            return IntegrationResult.fail("route", str(exc))

    def install_integration(self, definition: IntegrationDefinition) -> IntegrationResult:
        try:
            self.registry.register_provider(
                definition.integration_id, definition.to_dict()
            )
            self.metrics.increment("integrations.installed")
            self.events.emit(
                IntegrationEventType.INTEGRATION_INSTALLED,
                {"integration_id": definition.integration_id},
            )
            return IntegrationResult.ok(
                "install_integration", {"integration_id": definition.integration_id}
            )
        except Exception as exc:  # noqa: BLE001
            return IntegrationResult.fail("install_integration", str(exc))

    # --- Lifecycle --------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return self.runtime.status()

    def shutdown(self) -> None:
        self.runtime.stop()
