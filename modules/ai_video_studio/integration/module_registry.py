"""Module registry — registers and discovers studio services and sub-modules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RegisteredService:
    name: str
    service: Any
    kind: str
    description: str = ""
    version: str = "1.0"
    tags: list[str] = field(default_factory=list)


class ModuleRegistry:
    """A name-keyed registry of services and sub-module markers."""

    def __init__(self) -> None:
        self._services: dict[str, RegisteredService] = {}
        self._modules: set[str] = set()

    def register_service(
        self,
        name: str,
        service: Any,
        *,
        kind: str = "service",
        description: str = "",
        version: str = "1.0",
        tags: list[str] | None = None,
    ) -> None:
        """Register a service instance under ``name`` (replaces existing)."""
        self._services[name] = RegisteredService(
            name=name,
            service=service,
            kind=kind,
            description=description,
            version=version,
            tags=tags or [],
        )

    def register_module(self, name: str) -> None:
        self._modules.add(name)

    def get(self, name: str) -> Any | None:
        reg = self._services.get(name)
        return reg.service if reg else None

    def has(self, name: str) -> bool:
        return name in self._services

    def list_services(self) -> list[dict[str, Any]]:
        return [
            {
                "name": r.name,
                "kind": r.kind,
                "description": r.description,
                "version": r.version,
                "tags": r.tags,
            }
            for r in self._services.values()
        ]

    def list_modules(self) -> list[str]:
        return sorted(self._modules)

    def count(self) -> int:
        return len(self._services)


_registry: ModuleRegistry | None = None


def get_registry() -> ModuleRegistry:
    """Process-wide singleton registry."""
    global _registry
    if _registry is None:
        _registry = ModuleRegistry()
    return _registry
