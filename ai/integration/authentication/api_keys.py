"""
API Key Management
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class APIKey:
    key_id: str
    name: str
    key_hash: str
    scopes: list[str] = field(default_factory=list)
    rate_limit: int = 1000
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime | None = None
    use_count: int = 0


class APIKeyManager:
    def __init__(self):
        self.keys: dict[str, APIKey] = {}

    def generate_key(self, name: str, scopes: list[str] = None, rate_limit: int = 1000) -> tuple:
        raw_key = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_id = hashlib.sha256(name.encode()).hexdigest()[:16]
        api_key = APIKey(key_id=key_id, name=name, key_hash=key_hash, scopes=scopes or ["read"], rate_limit=rate_limit)
        self.keys[key_id] = api_key
        return raw_key, api_key

    def validate_key(self, raw_key: str) -> APIKey | None:
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        for key in self.keys.values():
            if key.key_hash == key_hash and key.is_active:
                key.last_used = datetime.now()
                key.use_count += 1
                return key
        return None

    def revoke_key(self, key_id: str) -> bool:
        key = self.keys.get(key_id)
        if key:
            key.is_active = False
            return True
        return False

    def get_key(self, key_id: str) -> APIKey | None:
        return self.keys.get(key_id)

    def list_keys(self) -> list[APIKey]:
        return list(self.keys.values())

    def count(self) -> int:
        return len(self.keys)
