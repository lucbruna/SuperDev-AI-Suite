"""
Integration Authentication - Core auth for integrations
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AuthType(Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC = "basic"
    CERTIFICATE = "certificate"
    HMAC = "hmac"


@dataclass
class AuthCredential:
    credential_id: str
    integration_id: str
    auth_type: AuthType
    key_hash: str = ""
    scopes: list[str] = field(default_factory=list)
    expires_at: datetime | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


class IntegrationAuth:
    def __init__(self):
        self.credentials: dict[str, AuthCredential] = {}
        self.active_sessions: dict[str, dict[str, Any]] = {}

    def create_credential(
        self, integration_id: str, auth_type: AuthType, secret: str = "", scopes: list[str] = None
    ) -> AuthCredential:
        credential_id = hashlib.sha256(
            f"{integration_id}{auth_type.value}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        key_hash = hashlib.sha256(secret.encode()).hexdigest() if secret else ""
        cred = AuthCredential(
            credential_id=credential_id,
            integration_id=integration_id,
            auth_type=auth_type,
            key_hash=key_hash,
            scopes=scopes or [],
        )
        self.credentials[credential_id] = cred
        return cred

    def validate_credential(self, credential_id: str, secret: str = "") -> bool:
        cred = self.credentials.get(credential_id)
        if not cred or not cred.is_active:
            return False
        if cred.expires_at and datetime.now() > cred.expires_at:
            return False
        return not (cred.key_hash and cred.key_hash != hashlib.sha256(secret.encode()).hexdigest())

    def revoke_credential(self, credential_id: str) -> bool:
        cred = self.credentials.get(credential_id)
        if cred:
            cred.is_active = False
            return True
        return False

    def authenticate(self, integration_id: str, auth_type: AuthType, credentials: dict[str, str]) -> str | None:
        for cred in self.credentials.values():
            if cred.integration_id == integration_id and cred.auth_type == auth_type and cred.is_active:
                session_token = secrets.token_urlsafe(32)
                self.active_sessions[session_token] = {
                    "credential_id": cred.credential_id,
                    "integration_id": integration_id,
                    "created_at": datetime.now().isoformat(),
                }
                return session_token
        return None

    def validate_session(self, token: str) -> bool:
        return token in self.active_sessions

    def invalidate_session(self, token: str) -> bool:
        if token in self.active_sessions:
            del self.active_sessions[token]
            return True
        return False

    def get_credentials(self, integration_id: str) -> list[AuthCredential]:
        return [c for c in self.credentials.values() if c.integration_id == integration_id]

    def count(self) -> int:
        return len(self.credentials)
