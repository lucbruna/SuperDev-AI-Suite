"""
Token Manager for Integration Auth
"""
import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class IntegrationToken:
    token_id: str
    integration_id: str
    token_type: str = "access"
    token_hash: str = ""
    scopes: list[str] = field(default_factory=list)
    expires_at: datetime | None = None
    is_revoked: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class IntegrationTokenManager:
    def __init__(self):
        self.tokens: dict[str, IntegrationToken] = {}
        self.access_ttl: int = 3600
        self.refresh_ttl: int = 86400

    def generate_token(self, integration_id: str, token_type: str = "access", scopes: list[str] = None) -> tuple:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_id = hashlib.sha256(f"{integration_id}{token_hash}".encode()).hexdigest()[:16]
        ttl = self.access_ttl if token_type == "access" else self.refresh_ttl
        token = IntegrationToken(token_id=token_id, integration_id=integration_id, token_type=token_type, token_hash=token_hash, scopes=scopes or [], expires_at=datetime.now() + timedelta(seconds=ttl))
        self.tokens[token_id] = token
        return raw_token, token

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

    def revoke_all(self, integration_id: str) -> int:
        count = 0
        for token in self.tokens.values():
            if token.integration_id == integration_id:
                token.is_revoked = True
                count += 1
        return count

    def get_tokens(self, integration_id: str) -> list[IntegrationToken]:
        return [t for t in self.tokens.values() if t.integration_id == integration_id]

    def count(self) -> int:
        return len(self.tokens)
