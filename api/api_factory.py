from __future__ import annotations

from typing import Any

from .api_registry import APIRegistry


class APIFactory:
    """Factory for creating API components."""

    def __init__(self, registry: APIRegistry) -> None:
        self._registry = registry
        self._builders: dict[str, Any] = {}

    def register_builder(self, name: str, builder: Any) -> None:
        self._builders[name] = builder

    def create(self, name: str, **kwargs: Any) -> Any:
        builder = self._builders.get(name)
        if builder is None:
            raise ValueError(f"Unknown component: {name}")
        instance = builder(**kwargs) if callable(builder) else builder
        self._registry.register_service(name, instance)
        return instance

    def create_many(self, definitions: list[tuple[str, Any]]) -> list[Any]:
        results = []
        for name, kwargs in definitions:
            results.append(self.create(name, **kwargs))
        return results

    def list_builders(self) -> list[str]:
        return list(self._builders.keys())

    def to_dict(self) -> dict[str, Any]:
        return {"builders": list(self._builders.keys()), "count": len(self._builders)}
