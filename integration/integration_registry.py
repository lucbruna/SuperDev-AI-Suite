from __future__ import annotations

import logging
from typing import Any, Callable


class IntegrationRegistry:
    """Registry of connectors, auth providers, transformers, and factories."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.registry")
        self._connectors: dict[str, Any] = {}
        self._auth_providers: dict[str, Any] = {}
        self._transformers: dict[str, Any] = {}
        self._webhook_handlers: dict[str, Any] = {}
        self._providers: dict[str, Any] = {}
        self._factories: dict[str, Callable[..., Any]] = {}

    # --- Connectors ---------------------------------------------------------

    def register_connector(self, name: str, connector: Any) -> None:
        self._connectors[name] = connector

    def get_connector(self, name: str) -> Any:
        return self._connectors.get(name)

    def list_connectors(self) -> list[str]:
        return sorted(self._connectors)

    # --- Auth providers ------------------------------------------------------

    def register_auth_provider(self, name: str, provider: Any) -> None:
        self._auth_providers[name] = provider

    def get_auth_provider(self, name: str) -> Any:
        return self._auth_providers.get(name)

    def list_auth_providers(self) -> list[str]:
        return sorted(self._auth_providers)

    # --- Transformers --------------------------------------------------------

    def register_transformer(self, name: str, transformer: Any) -> None:
        self._transformers[name] = transformer

    def get_transformer(self, name: str) -> Any:
        return self._transformers.get(name)

    def list_transformers(self) -> list[str]:
        return sorted(self._transformers)

    # --- Webhook handlers ----------------------------------------------------

    def register_webhook_handler(self, name: str, handler: Any) -> None:
        self._webhook_handlers[name] = handler

    def get_webhook_handler(self, name: str) -> Any:
        return self._webhook_handlers.get(name)

    # --- Providers (marketplace / integration definitions) ---------------------

    def register_provider(self, name: str, provider: Any) -> None:
        self._providers[name] = provider

    def get_provider(self, name: str) -> Any:
        return self._providers.get(name)

    def list_providers(self) -> list[str]:
        return sorted(self._providers)

    # --- Factories -------------------------------------------------------------

    def register_factory(self, name: str, factory: Callable[..., Any]) -> None:
        self._factories[name] = factory

    def get_factory(self, name: str) -> Callable[..., Any] | None:
        return self._factories.get(name)

    def snapshot(self) -> dict[str, int]:
        return {
            "connectors": len(self._connectors),
            "auth_providers": len(self._auth_providers),
            "transformers": len(self._transformers),
            "webhook_handlers": len(self._webhook_handlers),
            "providers": len(self._providers),
            "factories": len(self._factories),
        }
