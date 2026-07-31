"""OAuth provider integration."""
from __future__ import annotations

import time
import uuid
from typing import Any


class OAuthManager:
    def __init__(self) -> None:
        self._providers: dict[str, dict[str, Any]] = {}
        self._tokens: dict[str, dict[str, Any]] = {}
    def register_provider(self, name: str, client_id: str, scopes: list[str] | None = None) -> dict[str, Any]:
        self._providers[name] = {"client_id": client_id, "scopes": scopes or [], "enabled": True}
        return {"provider": name, "status": "registered"}
    def authorize(self, provider: str, user_id: str) -> dict[str, Any]:
        if provider not in self._providers:
            return {"error": "provider_not_found"}
        token_id = str(uuid.uuid4())[:12]
        self._tokens[token_id] = {"user_id": user_id, "provider": provider, "created_at": time.time()}
        return {"token_id": token_id, "user_id": user_id}
    def validate(self, token_id: str) -> bool:
        return token_id in self._tokens
    def revoke(self, token_id: str) -> bool:
        if token_id in self._tokens:
            del self._tokens[token_id]
            return True
        return False
    def list_providers(self) -> list[str]:
        return list(self._providers.keys())
