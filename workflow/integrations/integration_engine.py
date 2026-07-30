from __future__ import annotations

import logging
from typing import Any

from .integration_models import Integration, IntegrationStatus
from .integration_adapter import IntegrationAdapter
from .integration_http import IntegrationHttp
from .integration_auth import IntegrationAuth


class IntegrationEngine:
    """Central engine for external integrations."""

    def __init__(self) -> None:
        self._adapters: dict[str, IntegrationAdapter] = {}
        self._http = IntegrationHttp()
        self._auth = IntegrationAuth()
        self._log = logging.getLogger("superdev.workflow.integrations")

    def register(self, integration: Integration, adapter: IntegrationAdapter) -> None:
        self._adapters[integration.id] = adapter
        integration.status = IntegrationStatus.ACTIVE
        self._log.info("Registered integration %s", integration.id)

    def execute(self, integration_id: str, action: str, data: dict[str, Any] | None = None) -> Any:
        adapter = self._adapters.get(integration_id)
        if not adapter:
            raise ValueError(f"No adapter for integration {integration_id}")
        return adapter.execute(action, data or {})
