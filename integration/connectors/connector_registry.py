from __future__ import annotations

import logging
from typing import Any

from ..integration_registry import IntegrationRegistry


class ConnectorRegistry:
    """Registers connector providers by connector type."""

    def __init__(self, registry: IntegrationRegistry | None = None) -> None:
        self._log = logging.getLogger("superdev.integration.connectors.registry")
        self._registry = registry or IntegrationRegistry()
        self._classes: dict[str, type] = {}

    def register(self, connector_type: str, connector_class: type) -> None:
        self._classes[connector_type] = connector_class
        self._registry.register_connector(connector_type, connector_class)

    def get(self, connector_type: str) -> type | None:
        return self._classes.get(connector_type)

    def create(self, connector_type: str) -> Any | None:
        connector_class = self.get(connector_type)
        if connector_class is None:
            return None
        return connector_class()

    def list(self) -> list[str]:
        return sorted(self._classes)

    def has(self, connector_type: str) -> bool:
        return connector_type in self._classes

    def snapshot(self) -> dict[str, int]:
        return {"connector_types": len(self._classes)}
