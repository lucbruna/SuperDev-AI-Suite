from __future__ import annotations

from typing import Type

from backend.providers.base_provider import BaseProvider


class ProviderRegistry:
    """Registry for LLM provider implementations."""

    _providers: dict[str, Type[BaseProvider]] = {}
    _instances: dict[str, BaseProvider] = {}

    @classmethod
    def register(cls, name: str, provider_cls: Type[BaseProvider]) -> None:
        cls._providers[name] = provider_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseProvider] | None:
        return cls._providers.get(name)

    @classmethod
    def list_providers(cls) -> list[str]:
        return list(cls._providers.keys())

    @classmethod
    async def get_instance(cls, name: str, **kwargs) -> BaseProvider:
        if name not in cls._instances:
            provider_cls = cls._providers.get(name)
            if not provider_cls:
                raise ValueError(f"Unknown provider: {name}")
            cls._instances[name] = provider_cls(**kwargs)
        return cls._instances[name]

    @classmethod
    async def close_all(cls) -> None:
        for instance in cls._instances.values():
            await instance.close()
        cls._instances.clear()

    @classmethod
    def clear(cls) -> None:
        cls._instances.clear()
