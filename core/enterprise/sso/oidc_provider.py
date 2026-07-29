from __future__ import annotations as __

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from pydantic import BaseModel
import urllib.parse


class OIDCTokens(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str = ""
    token_type: str = "Bearer"
    expires_in: int = 3600


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    provider: str = "oidc"
    groups: list[str] = []


class OIDCProvider:
    def __init__(
        self,
        client_id: str = "",
        client_secret: str = "",
        issuer_url: str = "",
        authorization_url: str = "",
        token_url: str = "",
        userinfo_url: str = "",
        redirect_uri: str = "",
        scopes: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.client_id = client_id or f"oidc_{uuid4().hex[:8]}"
        self.client_secret = client_secret or uuid4().hex
        self.issuer_url = issuer_url or f"https://{uuid4().hex[:8]}.auth.example.com"
        self.authorization_url = authorization_url or f"{self.issuer_url}/authorize"
        self.token_url = token_url or f"{self.issuer_url}/token"
        self.userinfo_url = userinfo_url or f"{self.issuer_url}/userinfo"
        self.redirect_uri = redirect_uri or "http://localhost:8000/auth/callback"
        self.scopes = scopes or ["openid", "profile", "email"]

    async def get_auth_url(
        self, redirect_uri: str = "", state: str = ""
    ) -> str:
        await asyncio.sleep(0.01)
        state = state or uuid4().hex
        redirect = redirect_uri or self.redirect_uri
        params = urllib.parse.urlencode({
            "client_id": self.client_id,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "redirect_uri": redirect,
            "state": state,
        })
        return f"{self.authorization_url}?{params}"

    async def handle_callback(self, code: str) -> OIDCTokens:
        await asyncio.sleep(0.02)
        tokens = OIDCTokens(
            access_token=f"at_{uuid4().hex[:24]}",
            id_token=f"id_{uuid4().hex[:24]}",
            refresh_token=f"rt_{uuid4().hex[:24]}",
        )
        return tokens

    async def get_user_info(
        self, access_token: str
    ) -> UserInfo:
        await asyncio.sleep(0.01)
        user_id = f"oidc_user_{uuid4().hex[:8]}"
        return UserInfo(
            id=user_id,
            email=f"{user_id}@oidc.example.com",
            name="OIDC User",
            provider="oidc",
            groups=["users"],
        )

    async def refresh_token(self, refresh_token: str) -> OIDCTokens:
        await asyncio.sleep(0.02)
        return OIDCTokens(
            access_token=f"at_{uuid4().hex[:24]}",
            id_token=f"id_{uuid4().hex[:24]}",
            refresh_token=refresh_token,
        )

    async def decode_id_token(self, id_token: str) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        return {
            "sub": f"user_{uuid4().hex[:8]}",
            "iss": self.issuer_url,
            "aud": self.client_id,
            "exp": int(datetime.utcnow().timestamp()) + 3600,
            "iat": int(datetime.utcnow().timestamp()),
        }
