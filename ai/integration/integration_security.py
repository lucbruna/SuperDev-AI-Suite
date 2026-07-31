"""
Integration Security - Security controls for integrations
"""
import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AuthMethod(Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    CERTIFICATE = "certificate"
    HMAC = "hmac"


@dataclass
class SecurityPolicy:
    policy_id: str
    name: str
    auth_methods: list[AuthMethod] = field(default_factory=list)
    rate_limit: int = 1000
    ip_whitelist: list[str] = field(default_factory=list)
    ip_blacklist: list[str] = field(default_factory=list)
    encryption_required: bool = True
    audit_logging: bool = True
    max_payload_size: int = 10 * 1024 * 1024
    enabled: bool = True


@dataclass
class SecurityToken:
    token_id: str
    integration_id: str
    auth_method: AuthMethod
    token_hash: str = ""
    expires_at: datetime | None = None
    scopes: list[str] = field(default_factory=list)
    is_revoked: bool = False


class IntegrationSecurity:
    def __init__(self):
        self.policies: dict[str, SecurityPolicy] = {}
        self.tokens: dict[str, SecurityToken] = {}
        self.blocked_ips: set[str] = set()
        self.audit_log: list[dict[str, Any]] = []
        self.rate_counters: dict[str, int] = {}

    def create_policy(self, name: str, auth_methods: list[AuthMethod] = None, **kwargs) -> SecurityPolicy:
        policy_id = hashlib.sha256(name.encode()).hexdigest()[:16]
        policy = SecurityPolicy(policy_id=policy_id, name=name, auth_methods=auth_methods or [AuthMethod.API_KEY], **kwargs)
        self.policies[policy_id] = policy
        return policy

    def create_token(self, integration_id: str, auth_method: AuthMethod, scopes: list[str] = None) -> SecurityToken:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token = SecurityToken(token_id=hashlib.sha256(f"{integration_id}{token_hash}".encode()).hexdigest()[:16], integration_id=integration_id, auth_method=auth_method, token_hash=token_hash, scopes=scopes or [])
        self.tokens[token.token_id] = token
        return token

    def validate_token(self, token_id: str) -> bool:
        token = self.tokens.get(token_id)
        if not token or token.is_revoked:
            return False
        return not (token.expires_at and datetime.now() > token.expires_at)

    def revoke_token(self, token_id: str) -> bool:
        token = self.tokens.get(token_id)
        if token:
            token.is_revoked = True
            return True
        return False

    def block_ip(self, ip: str) -> None:
        self.blocked_ips.add(ip)

    def unblock_ip(self, ip: str) -> bool:
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            return True
        return False

    def is_ip_blocked(self, ip: str) -> bool:
        return ip in self.blocked_ips

    def check_rate_limit(self, integration_id: str, limit: int = 1000) -> bool:
        count = self.rate_counters.get(integration_id, 0)
        if count >= limit:
            return False
        self.rate_counters[integration_id] = count + 1
        return True

    def reset_rate_limit(self, integration_id: str) -> None:
        self.rate_counters[integration_id] = 0

    def audit(self, action: str, integration_id: str, details: dict[str, Any] = None) -> None:
        self.audit_log.append({"action": action, "integration_id": integration_id, "details": details or {}, "timestamp": datetime.now().isoformat()})

    def get_audit_log(self, integration_id: str = None) -> list[dict[str, Any]]:
        if integration_id:
            return [e for e in self.audit_log if e["integration_id"] == integration_id]
        return self.audit_log

    def get_policy(self, policy_id: str) -> SecurityPolicy | None:
        return self.policies.get(policy_id)

    def count(self) -> int:
        return len(self.tokens)
