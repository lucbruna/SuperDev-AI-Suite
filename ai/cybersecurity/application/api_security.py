"""
API Security
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class APIKeyState(Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class APIKey:
    key_id: str
    key_hash: str
    name: str
    state: APIKeyState = APIKeyState.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    scopes: list[str] = field(default_factory=list)
    rate_limit: int = 1000


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_at: datetime | None = None
    retry_after: int = 0


class APISecurity:
    def __init__(self):
        self.api_keys: dict[str, APIKey] = {}
        self.rate_counters: dict[str, int] = {}
        self.cors_origins: list[str] = ["*"]
        self.blocked_ips: set = set()

    def generate_api_key(self, name: str, scopes: list[str] = None, rate_limit: int = 1000) -> tuple[str, APIKey]:
        key_id = secrets.token_hex(16)
        raw_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = APIKey(key_id=key_id, key_hash=key_hash, name=name, scopes=scopes or [], rate_limit=rate_limit)
        self.api_keys[key_id] = api_key
        return raw_key, api_key

    def validate_api_key(self, raw_key: str) -> APIKey | None:
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        for key in self.api_keys.values():
            if key.key_hash == key_hash and key.state == APIKeyState.ACTIVE:
                return key
        return None

    def revoke_api_key(self, key_id: str) -> bool:
        key = self.api_keys.get(key_id)
        if key:
            key.state = APIKeyState.REVOKED
            return True
        return False

    def check_rate_limit(self, key_id: str) -> RateLimitResult:
        key = self.api_keys.get(key_id)
        if not key:
            return RateLimitResult(allowed=False, remaining=0)
        count = self.rate_counters.get(key_id, 0)
        if count >= key.rate_limit:
            return RateLimitResult(allowed=False, remaining=0, retry_after=60)
        self.rate_counters[key_id] = count + 1
        return RateLimitResult(allowed=True, remaining=key.rate_limit - count - 1)

    def reset_rate_limit(self, key_id: str) -> None:
        self.rate_counters[key_id] = 0

    def set_cors_origins(self, origins: list[str]) -> None:
        self.cors_origins = origins

    def check_cors(self, origin: str) -> bool:
        return "*" in self.cors_origins or origin in self.cors_origins

    def block_ip(self, ip: str) -> None:
        self.blocked_ips.add(ip)

    def is_ip_blocked(self, ip: str) -> bool:
        return ip in self.blocked_ips

    def sign_request(self, data: str, secret: str) -> str:
        return hashlib.sha256((data + secret).encode()).hexdigest()

    def verify_signature(self, data: str, secret: str, signature: str) -> bool:
        expected = self.sign_request(data, secret)
        return secrets.compare_digest(expected, signature)

    def count(self) -> int:
        return len(self.api_keys)
