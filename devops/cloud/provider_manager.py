from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cloud_engine import CloudEngine


class ProviderManager:
    """Manages cloud providers — registration, selection, credentials."""

    def __init__(self, engine: CloudEngine) -> None:
        self._log = logging.getLogger("superdev.devops.cloud.providers")
        self._engine = engine
        self._providers: dict[str, Any] = {}
        self._credentials: dict[str, dict[str, str]] = {}

    def register(self, name: str, provider: Any) -> None:
        self._providers[name] = provider

    def get(self, name: str) -> Any:
        return self._providers.get(name)

    def list(self) -> list[str]:
        return list(self._providers.keys())

    def configure_credentials(self, provider: str, credentials: dict[str, str]) -> bool:
        """Store credentials for a provider. Returns True when the provider exists."""
        if provider not in self._providers:
            return False
        self._credentials[provider] = dict(credentials)
        return True

    def validate_credentials(self, provider: str) -> bool:
        """Credentials are valid when the provider is registered and configured."""
        return provider in self._providers and bool(self._credentials.get(provider))
