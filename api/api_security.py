from __future__ import annotations

from typing import Any

from .api_interfaces import IAPIAuthenticator


class APISecurity(IAPIAuthenticator):
    """API security: authentication, encryption, and input sanitization."""

    def __init__(self) -> None:
        self._api_keys: dict[str, dict[str, Any]] = {}
        self._blocked_ips: set[str] = set()
        self._blocked_tokens: set[str] = set()

    def register_api_key(self, key: str, metadata: dict[str, Any] | None = None) -> None:
        self._api_keys[key] = metadata or {}

    def revoke_api_key(self, key: str) -> bool:
        return self._api_keys.pop(key, None) is not None

    def block_ip(self, ip: str) -> None:
        self._blocked_ips.add(ip)

    def unblock_ip(self, ip: str) -> None:
        self._blocked_ips.discard(ip)

    def is_ip_blocked(self, ip: str) -> bool:
        return ip in self._blocked_ips

    def block_token(self, token: str) -> None:
        self._blocked_tokens.add(token)

    def is_token_blocked(self, token: str) -> bool:
        return token in self._blocked_tokens

    def sanitize_input(self, data: str) -> str:
        import html
        return html.escape(data)

    async def authenticate(self, request: Any) -> dict[str, Any]:
        headers = getattr(request, "headers", {})
        api_key = headers.get("X-API-Key", "") if isinstance(headers, dict) else headers.get("X-API-Key")
        if api_key and api_key in self._api_keys:
            return {"authenticated": True, "method": "api_key", "metadata": self._api_keys.get(api_key, {})}
        return {"authenticated": False, "method": "none", "error": "Missing or invalid API key"}

    async def validate_token(self, token: str) -> dict[str, Any]:
        if self.is_token_blocked(token):
            return {"valid": False, "error": "Token blocked"}
        return {"valid": True}

    def to_dict(self) -> dict[str, Any]:
        return {"api_keys": len(self._api_keys), "blocked_ips": len(self._blocked_ips), "blocked_tokens": len(self._blocked_tokens)}
