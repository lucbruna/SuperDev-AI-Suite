"""Service locator — resolve studio services by name from the registry."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.integration.module_registry import get_registry


class ServiceNotFoundError(LookupError):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Service '{name}' is not registered")


class ServiceLocator:
    """Thin resolver over the shared ModuleRegistry."""

    def __init__(self, registry=None) -> None:  # type: ignore[no-untyped-def]
        self._registry = registry or get_registry()

    def resolve(self, name: str) -> Any:
        """Return the service instance, raising ServiceNotFoundError if absent."""
        service = self._registry.get(name)
        if service is None:
            raise ServiceNotFoundError(name)
        return service

    def try_resolve(self, name: str) -> Any | None:
        return self._registry.get(name)

    def resolve_many(self, *names: str) -> dict[str, Any]:
        """Resolve several services; missing ones are simply skipped."""
        return {n: s for n in names if (s := self._registry.get(n)) is not None}

    def available(self) -> list[str]:
        return [r["name"] for r in self._registry.list_services()]


_default_locator: ServiceLocator | None = None


def get_service_locator() -> ServiceLocator:
    global _default_locator
    if _default_locator is None:
        _default_locator = ServiceLocator()
    return _default_locator
