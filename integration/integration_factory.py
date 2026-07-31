from __future__ import annotations

import logging
from typing import Any

from .integration_config import IntegrationConfig
from .integration_manager import IntegrationManager
from .integration_registry import IntegrationRegistry


class IntegrationFactory:
    """Builds integration components from configuration and registry providers."""

    def __init__(
        self,
        config: IntegrationConfig | None = None,
        registry: IntegrationRegistry | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.integration.factory")
        self.config = config or IntegrationConfig()
        self.registry = registry or IntegrationRegistry()

    def build_connector(self, connector_type: str) -> Any:
        """Returns a connector instance by type, building one from registered
        connector classes when available (the default connector is a generic
        in-memory connector useful for tests and local workflows).
        """
        connector = self.registry.get_connector(connector_type)
        if connector is not None:
            return connector() if isinstance(connector, type) else connector

        factory = self.registry.get_factory(f"connector:{connector_type}")
        if factory is not None:
            return factory(self.config)

        from .connectors.connector_template import GenericConnector

        return GenericConnector(connector_type)

    def build_auth_provider(self, method: str) -> Any:
        provider = self.registry.get_auth_provider(method)
        if provider is not None:
            return provider() if isinstance(provider, type) else provider

        factory = self.registry.get_factory(f"auth:{method}")
        if factory is not None:
            return factory(self.config)

        from .authentication.api_key import APIKeyProvider

        return APIKeyProvider()

    def build_transformer(self, name: str | None = None) -> Any:
        transformer = self.registry.get_transformer(name or "default")
        if transformer is not None:
            return transformer() if isinstance(transformer, type) else transformer

        from .transformation.mapper import DataMapper

        return DataMapper()

    def build_manager(self) -> IntegrationManager:
        return IntegrationManager(
            config=self.config,
            registry=self.registry,
        )
