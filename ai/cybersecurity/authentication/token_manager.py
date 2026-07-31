"""
Token Manager
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import secrets
import hashlib
import json


@dataclass
class Token:
    token_id: str
    user_id: str
    token_type: str = "access"
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    scopes: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_revoked: bool = False
    
    @property
    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False


class TokenManager:
    def __init__(self, access_ttl: int = 3600, refresh_ttl: int = 86400):
        self.tokens: Dict[str, Token] = {}
        self.access_ttl = access_ttl
        self.refresh_ttl = refresh_ttl
        
    def generate_access_token(self, user_id: str, scopes: list = None) -> Token:
        token = Token(
            token_id=secrets.token_hex(32),
            user_id=user_id,
            token_type="access",
            expires_at=datetime.now() + timedelta(seconds=self.access_ttl),
            scopes=scopes or []
        )
        self.tokens[token.token_id] = token
        return token
        
    def generate_refresh_token(self, user_id: str) -> Token:
        token = Token(
            token_id=secrets.token_hex(32),
            user_id=user_id,
            token_type="refresh",
            expires_at=datetime.now() + timedelta(seconds=self.refresh_ttl)
        )
        self.tokens[token.token_id] = token
        return token
        
    def validate_token(self, token_id: str) -> bool:
        token = self.tokens.get(token_id)
        if not token:
            return False
        return not token.is_revoked and not token.is_expired
        
    def revoke_token(self, token_id: str) -> bool:
        token = self.tokens.get(token_id)
        if token:
            token.is_revoked = True
            return True
        return False
        
    def revoke_all_user(self, user_id: str) -> int:
        count = 0
        for token in self.tokens.values():
            if token.user_id == user_id:
                token.is_revoked = True
                count += 1
        return count
        
    def get_user_tokens(self, user_id: str) -> list:
        return [t for t in self.tokens.values() if t.user_id == user_id and not t.is_revoked]
        
    def cleanup_expired(self) -> int:
        expired = [tid for tid, t in self.tokens.items() if t.is_expired]
        for tid in expired:
            del self.tokens[tid]
        return len(expired)
        
    def count(self) -> int:
        return sum(1 for t in self.tokens.values() if not t.is_revoked)
