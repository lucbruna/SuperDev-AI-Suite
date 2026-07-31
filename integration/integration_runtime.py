from __future__ import annotations

import logging
from typing import Any

from .integration_config import IntegrationConfig
from .integration_events import IntegrationEvents
from .integration_factory import IntegrationFactory
from .integration_manager import IntegrationManager
from .integration_metrics import IntegrationMetrics
from .integration_registry import IntegrationRegistry
from .integration_security import IntegrationSecurity


class IntegrationRuntime:
    """Runtime lifecycle and composition root for the integration engine."""

    def __init__(self, config: IntegrationConfig | None = None) -> None:
        self._log = logging.getLogger("superdev.integration.runtime")
        self.config = config or IntegrationConfig()
        self.events = IntegrationEvents()
        self.metrics = IntegrationMetrics()
        self.registry = IntegrationRegistry()
        self.security = IntegrationSecurity(self.config.enable_auth)
        self.manager: IntegrationManager | None = None
        self.factory: IntegrationFactory | None = None
        self._started = False

    def start(self) -> "IntegrationRuntime":
        if self._started:
            return self
        self.factory = IntegrationFactory(self.config, self.registry)
        self.manager = self.factory.build_manager()
        self._started = True
        self._log.info(
            "integration runtime started (workspace=%s, gateway=%s:%s)",
            self.config.workspace_id,
            self.config.gateway_host,
            self.config.gateway_port,
        )
        return self

    def stop(self) -> None:
        if self.manager is not None:
            self.manager.shutdown()
        self._started = False
        self._log.info("integration runtime stopped")

    def status(self) -> dict[str, Any]:
        manager = self.manager
        base = {
            "started": self._started,
            "workspace_id": self.config.workspace_id,
            "gateway": f"{self.config.gateway_host}:{self.config.gateway_port}",
        }
        if manager is not None:
            base.update(manager.status())
        return base

    @property
    def is_running(self) -> bool:
        return self._started and self.manager is not None
