from __future__ import annotations

from typing import Any


class ProviderPluginRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, type] = {}

    def register_provider(self, name: str, provider_class: type) -> None:
        if name in self._providers:
            raise ValueError(f"Provider '{name}' is already registered")
        self._providers[name] = provider_class

    def get_provider(self, name: str) -> type | None:
        return self._providers.get(name)

    def list_providers(self) -> list[dict[str, Any]]:
        return [
            {"name": name, "provider_class": cls}
            for name, cls in self._providers.items()
        ]
