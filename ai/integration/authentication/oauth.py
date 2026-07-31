"""
OAuth 2.0 Provider
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import secrets


@dataclass
class OAuthApp:
    app_id: str
    name: str
    client_id: str
    client_secret: str
    redirect_uris: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class OAuthToken:
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: str = ""
    scope: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class OAuthProvider:
    def __init__(self):
        self.apps: Dict[str, OAuthApp] = {}
        self.tokens: Dict[str, OAuthToken] = {}
        self.authorization_codes: Dict[str, Dict[str, Any]] = {}

    def register_app(self, name: str, redirect_uris: List[str] = None, scopes: List[str] = None) -> OAuthApp:
        client_id = secrets.token_urlsafe(32)
        client_secret = secrets.token_urlsafe(64)
        app = OAuthApp(app_id=hashlib.sha256(client_id.encode()).hexdigest()[:16], name=name, client_id=client_id, client_secret=client_secret, redirect_uris=redirect_uris or [], scopes=scopes or ["read"])
        self.apps[app.app_id] = app
        return app

    def generate_auth_code(self, app_id: str, user_id: str, scope: str = "read") -> Optional[str]:
        app = self.apps.get(app_id)
        if not app or not app.is_active:
            return None
        code = secrets.token_urlsafe(32)
        self.authorization_codes[code] = {"app_id": app_id, "user_id": user_id, "scope": scope, "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()}
        return code

    def exchange_code(self, code: str, client_id: str, client_secret: str) -> Optional[OAuthToken]:
        code_data = self.authorization_codes.pop(code, None)
        if not code_data:
            return None
        app = self.apps.get(code_data["app_id"])
        if not app or app.client_id != client_id or app.client_secret != client_secret:
            return None
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        token = OAuthToken(access_token=access_token, refresh_token=refresh_token, scope=code_data["scope"])
        self.tokens[access_token] = token
        return token

    def validate_token(self, access_token: str) -> bool:
        token = self.tokens.get(access_token)
        if not token:
            return False
        elapsed = (datetime.now() - token.created_at).total_seconds()
        return elapsed < token.expires_in

    def revoke_token(self, access_token: str) -> bool:
        if access_token in self.tokens:
            del self.tokens[access_token]
            return True
        return False

    def get_app(self, app_id: str) -> Optional[OAuthApp]:
        return self.apps.get(app_id)

    def count(self) -> int:
        return len(self.apps)
