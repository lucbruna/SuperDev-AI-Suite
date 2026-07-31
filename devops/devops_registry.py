from __future__ import annotations

from typing import Any


class DevOpsRegistry:
    """Registry for DevOps services, providers, and resources."""

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}
        self._providers: dict[str, Any] = {}
        self._resources: dict[str, Any] = {}

    def register_service(self, name: str, service: Any) -> None:
        self._services[name] = service

    def register_provider(self, name: str, provider: Any) -> None:
        self._providers[name] = provider

    def register_resource(self, name: str, resource: Any) -> None:
        self._resources[name] = resource

    def get_service(self, name: str) -> Any:
        return self._services.get(name)

    def get_provider(self, name: str) -> Any:
        return self._providers.get(name)

    def list_services(self) -> dict[str, Any]:
        return dict(self._services)

    def list_providers(self) -> dict[str, Any]:
        return dict(self._providers)

    @property
    def size(self) -> int:
        return len(self._services) + len(self._providers) + len(self._resources)
