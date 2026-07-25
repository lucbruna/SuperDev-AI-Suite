from __future__ import annotations
from typing import Optional
from .base_provider import BaseProvider


class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, type[BaseProvider]] = {}
        self._instances: dict[str, BaseProvider] = {}

    def register(self, name: str, provider_class: type[BaseProvider]) -> None:
        self._providers[name] = provider_class

    def register_instance(self, name: str, instance: BaseProvider) -> None:
        self._instances[name] = instance

    def get(self, name: str) -> Optional[BaseProvider]:
        if name in self._instances:
            return self._instances[name]
        cls = self._providers.get(name)
        if cls is None:
            return None
        return cls

    def list(self) -> list[str]:
        return list(self._providers.keys()) + list(self._instances.keys())

    def get_by_capability(self, capability: str) -> list[BaseProvider]:
        result = []
        for instance in self._instances.values():
            try:
                models = instance.list_models()
                if callable(models):
                    import asyncio
                    models = asyncio.run(models)
            except Exception:
                continue
        return result

    def unregister(self, name: str) -> None:
        self._providers.pop(name, None)
        self._instances.pop(name, None)
