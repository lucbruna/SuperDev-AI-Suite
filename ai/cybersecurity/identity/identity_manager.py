"""
Identity Manager
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class IdentityProvider:
    name: str
    provider_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class IdentityManager:
    def __init__(self):
        self.providers: Dict[str, IdentityProvider] = {}
        self.mappings: Dict[str, str] = {}
        
    def add_provider(self, name: str, provider_type: str, config: Dict[str, Any] = None) -> IdentityProvider:
        provider = IdentityProvider(name=name, provider_type=provider_type, config=config or {})
        self.providers[name] = provider
        return provider
        
    def get_provider(self, name: str) -> Optional[IdentityProvider]:
        return self.providers.get(name)
        
    def list_providers(self) -> List[IdentityProvider]:
        return list(self.providers.values())
        
    def map_identity(self, external_id: str, internal_id: str) -> None:
        self.mappings[external_id] = internal_id
        
    def resolve_identity(self, external_id: str) -> Optional[str]:
        return self.mappings.get(external_id)
        
    def count(self) -> int:
        return len(self.providers)
