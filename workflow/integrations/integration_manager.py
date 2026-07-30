from __future__ import annotations

import logging
from typing import Any

from .integration_models import Integration, IntegrationStatus


class IntegrationManager:
    """Manages integration lifecycle."""

    def __init__(self) -> None:
        self._integrations: dict[str, Integration] = {}
        self._log = logging.getLogger("superdev.workflow.integrations.manager")

    def add(self, integration: Integration) -> None:
        self._integrations[integration.id] = integration
        self._log.info("Added integration %s (%s)", integration.id, integration.name)

    def remove(self, integration_id: str) -> None:
        self._integrations.pop(integration_id, None)

    def get(self, integration_id: str) -> Integration | None:
        return self._integrations.get(integration_id)

    def list_active(self) -> list[Integration]:
        return [i for i in self._integrations.values() if i.status == IntegrationStatus.ACTIVE]
