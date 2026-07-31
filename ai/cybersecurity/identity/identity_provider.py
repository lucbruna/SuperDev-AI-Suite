"""
Identity Provider Integration
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderType(Enum):
    LDAP = "ldap"
    SAML = "saml"
    OAUTH2 = "oauth2"
    OIDC = "oidc"
    ACTIVE_DIRECTORY = "active_directory"


@dataclass
class IdentityProviderConfig:
    name: str
    provider_type: ProviderType
    endpoint: str = ""
    client_id: str = ""
    client_secret: str = ""
    settings: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class IdentityProviderManager:
    def __init__(self):
        self.providers: dict[str, IdentityProviderConfig] = {}

    def add_provider(self, name: str, provider_type: ProviderType, **kwargs) -> IdentityProviderConfig:
        provider = IdentityProviderConfig(name=name, provider_type=provider_type, **kwargs)
        self.providers[name] = provider
        return provider

    def get_provider(self, name: str) -> IdentityProviderConfig | None:
        return self.providers.get(name)

    def list_providers(self) -> list[IdentityProviderConfig]:
        return list(self.providers.values())

    def list_by_type(self, provider_type: ProviderType) -> list[IdentityProviderConfig]:
        return [p for p in self.providers.values() if p.provider_type == provider_type]

    def authenticate(self, provider_name: str, credentials: dict[str, Any]) -> bool:
        provider = self.get_provider(provider_name)
        return bool(provider and provider.enabled)

    def count(self) -> int:
        return len(self.providers)
