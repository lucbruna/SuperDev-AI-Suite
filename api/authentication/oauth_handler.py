from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from typing import Any

from ..api_interfaces import IAPIAuthenticator


class OAuthHandler(IAPIAuthenticator):
    """OAuth 2.0 / OIDC authentication handler."""

    PROVIDER_CONFIGS: dict[str, dict[str, str]] = {
        "google": {
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
            "scopes": "openid email profile",
        },
        "github": {
            "authorize_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "scopes": "read:user user:email",
        },
        "microsoft": {
            "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "userinfo_url": "https://graph.microsoft.com/v1.0/me",
            "scopes": "User.Read openid profile",
        },
    }

    def __init__(self, client_id: str = "", client_secret: str = "") -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._providers: dict[str, dict[str, str]] = dict(self.PROVIDER_CONFIGS)

    def register_provider(self, name: str, config: dict[str, str]) -> None:
        self._providers[name] = config

    def authorize_url(self, provider: str, redirect_uri: str, state: str = "") -> str:
        config = self._providers.get(provider)
        if config is None:
            raise ValueError(f"Unknown provider: {provider}")
        params = {
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": config.get("scopes", ""),
            "state": state or "",
        }
        return f"{config['authorize_url']}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, provider: str, code: str, redirect_uri: str, client_secret: str) -> dict[str, Any]:
        config = self._providers.get(provider)
        if config is None:
            return {"error": f"Unknown provider: {provider}"}
        data = {
            "client_id": self._client_id,
            "client_secret": client_secret or self._client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        try:
            req = urllib.request.Request(
                config["token_url"],
                data=urllib.parse.urlencode(data).encode(),
                headers={"Accept": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result: dict[str, Any] = json.loads(resp.read().decode())
                return result
        except Exception as e:
            return {"error": str(e)}

    def refresh_token(self, provider: str, refresh_token: str) -> dict[str, Any]:
        config = self._providers.get(provider)
        if config is None:
            return {"error": f"Unknown provider: {provider}"}
        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        try:
            req = urllib.request.Request(
                config["token_url"],
                data=urllib.parse.urlencode(data).encode(),
                headers={"Accept": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result: dict[str, Any] = json.loads(resp.read().decode())
                return result
        except Exception as e:
            return {"error": str(e)}

    def validate_id_token(self, id_token: str, client_id: str, issuer: str) -> dict[str, Any]:
        import base64
        try:
            parts = id_token.split(".")
            if len(parts) != 3:
                return {"valid": False, "error": "Invalid token format"}
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
            now = time.time()
            if payload.get("exp", 0) < now:
                return {"valid": False, "error": "Token expired"}
            if payload.get("aud") != client_id:
                return {"valid": False, "error": "Invalid audience"}
            return {"valid": True, "payload": payload}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def authenticate(self, request: Any) -> dict[str, Any]:
        return {"authenticated": False, "method": "oauth", "error": "OAuth requires interactive flow"}

    async def validate_token(self, token: str) -> dict[str, Any]:
        return self.validate_id_token(token, self._client_id, "")

    def to_dict(self) -> dict[str, Any]:
        return {
            "providers": list(self._providers.keys()),
            "client_id_configured": bool(self._client_id),
        }
