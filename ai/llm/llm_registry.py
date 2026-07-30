from __future__ import annotations

from typing import Any

from .llm_interfaces import ILLMProvider, ILLMRegistry
from .llm_models import ProviderInfo, ProviderState


class LLMRegistry(ILLMRegistry):
    """Central registry for LLM provider discovery and lookup."""

    def __init__(self) -> None:
        self._providers: dict[str, ILLMProvider] = {}
        self._info: dict[str, ProviderInfo] = {}

    def register(self, provider: ILLMProvider) -> str:
        name = provider.name()
        self._providers[name] = provider
        if name not in self._info:
            self._info[name] = ProviderInfo(name=name, model=provider.model())
        return name

    def register_with_info(self, provider: ILLMProvider, info: ProviderInfo) -> str:
        name = self.register(provider)
        self._info[name] = info
        return name

    def unregister(self, name: str) -> bool:
        if name in self._providers:
            del self._providers[name]
            self._info.pop(name, None)
            return True
        return False

    def get(self, name: str) -> ILLMProvider | None:
        return self._providers.get(name)

    def get_info(self, name: str) -> ProviderInfo | None:
        return self._info.get(name)

    def list_providers(self) -> list[ILLMProvider]:
        return list(self._providers.values())

    def list_names(self) -> list[str]:
        return list(self._providers.keys())

    def update_state(self, name: str, state: ProviderState) -> None:
        if name in self._info:
            self._info[name].state = state

    @property
    def active_providers(self) -> list[str]:
        return [n for n, i in self._info.items() if i.state == ProviderState.ACTIVE]

    @property
    def provider_count(self) -> int:
        return len(self._providers)

    def to_dict(self) -> dict[str, Any]:
        return {
            "providers": list(self._providers.keys()),
            "provider_count": self.provider_count,
            "active": self.active_providers,
        }
