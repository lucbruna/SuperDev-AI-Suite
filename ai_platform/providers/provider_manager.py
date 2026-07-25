from __future__ import annotations
from typing import Optional
import asyncio

from .base_provider import BaseProvider, HealthStatus
from .provider_configuration import ProviderConfig
from .provider_registry import ProviderRegistry
from .provider_factory import ProviderFactory
from .provider_health import HealthChecker


class ProviderManager:
    def __init__(self):
        self.registry = ProviderRegistry()
        self.factory = ProviderFactory()
        self.health_checker = HealthChecker()
        self._initialized = False

    def initialize_all(self, configs: list[ProviderConfig]) -> None:
        for cfg in configs:
            provider = self.factory.create(cfg)
            self.registry.register_instance(cfg.name, provider)
        self._initialized = True

    def get_provider(self, name: str) -> BaseProvider:
        provider = self.registry.get(name)
        if provider is None:
            raise ValueError(f"Provider '{name}' not found. Available: {self.registry.list()}")
        return provider

    def get_healthy_providers(self) -> list[BaseProvider]:
        results = []
        for name in self.registry.list():
            try:
                p = self.registry.get(name)
                if isinstance(p, BaseProvider):
                    if asyncio.run(self.health_checker.check(p)):
                        results.append(p)
            except Exception:
                continue
        return results

    def get_providers_by_capability(self, capability: str) -> list[BaseProvider]:
        return self.registry.get_by_capability(capability)

    async def health_check_all(self) -> dict[str, HealthStatus]:
        results = {}
        for name in self.registry.list():
            p = self.registry.get(name)
            if isinstance(p, BaseProvider):
                try:
                    status = await p.health()
                    results[name] = status
                except Exception as e:
                    results[name] = HealthStatus(status="unhealthy", error=str(e))
        return results
