"""
Identity Manager
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IdentityProvider:
    name: str
    provider_type: str
    config: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class IdentityManager:
    def __init__(self):
        self.providers: dict[str, IdentityProvider] = {}
        self.mappings: dict[str, str] = {}

    def add_provider(self, name: str, provider_type: str, config: dict[str, Any] = None) -> IdentityProvider:
        provider = IdentityProvider(name=name, provider_type=provider_type, config=config or {})
        self.providers[name] = provider
        return provider

    def get_provider(self, name: str) -> IdentityProvider | None:
        return self.providers.get(name)

    def list_providers(self) -> list[IdentityProvider]:
        return list(self.providers.values())

    def map_identity(self, external_id: str, internal_id: str) -> None:
        self.mappings[external_id] = internal_id

    def resolve_identity(self, external_id: str) -> str | None:
        return self.mappings.get(external_id)

    def count(self) -> int:
        return len(self.providers)
