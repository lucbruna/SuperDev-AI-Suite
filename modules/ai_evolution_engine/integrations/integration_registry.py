"""Integration registry: lazy, gracefully-degrading connectors to sibling modules."""
from __future__ import annotations

import importlib
from typing import Any

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


class IntegrationConnector:
    """Base connector. Subclasses implement availability + collection."""

    name: str = ""
    description: str = ""

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description

    def check_available(self) -> bool:
        return False

    def collect(self, ctx: EvolutionContext) -> dict[str, Any]:
        return {"available": self.check_available(), "name": self.name}


class ModuleConnector(IntegrationConnector):
    """Connector that lazily imports a sibling module."""

    module: str = ""
    public_api: tuple[str, ...] = ()

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        module: str | None = None,
        public_api: tuple[str, ...] | None = None,
    ) -> None:
        super().__init__(name=name, description=description)
        if module is not None:
            self.module = module
        if public_api is not None:
            self.public_api = tuple(public_api)

    def check_available(self) -> bool:
        try:
            importlib.import_module(self.module)
            return True
        except Exception:
            return False

    def import_module(self):
        try:
            return importlib.import_module(self.module)
        except Exception:
            return None

    def collect(self, ctx: EvolutionContext) -> dict[str, Any]:
        module = self.import_module()
        if module is None:
            return {"available": False, "name": self.name}
        payload: dict[str, Any] = {"available": True, "name": self.name}
        for attr in self.public_api:
            if hasattr(module, attr):
                payload[attr] = getattr(module, attr)
        return payload


class IntegrationRegistry:
    """Registers connectors and collects integration status/artifacts."""

    def __init__(self) -> None:
        self._connectors: dict[str, IntegrationConnector] = {}

    def register(self, connector: IntegrationConnector) -> None:
        self._connectors[connector.name] = connector

    def unregister(self, name: str) -> None:
        self._connectors.pop(name, None)

    def get(self, name: str) -> IntegrationConnector | None:
        return self._connectors.get(name)

    def names(self) -> list[str]:
        return sorted(self._connectors)

    def available(self, name: str) -> bool:
        connector = self._connectors.get(name)
        if connector is None:
            return False
        return connector.check_available()

    def available_connectors(self) -> list[str]:
        return [name for name in self.names() if self.available(name)]

    def collect_all(self, ctx: EvolutionContext) -> dict[str, dict[str, Any]]:
        return {name: self._connectors[name].collect(ctx) for name in self.names()}

    def summary(self) -> dict[str, bool]:
        return {name: self.available(name) for name in self.names()}
