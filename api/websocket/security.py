from __future__ import annotations

import time
from typing import Any

from ..api_interfaces import IAPIAuthenticator
from ..api_logger import APILogger


class WebSocketSecurity:
    """Origin and token validation helpers."""

    def __init__(self, authenticator: IAPIAuthenticator | None = None, logger: APILogger | None = None) -> None:
        self._authenticator = authenticator
        self._logger = logger or APILogger("ws.security")

    def validate_origin(self, origin: str, allowed_origins: list[str]) -> bool:
        if not allowed_origins:
            return True
        return origin in allowed_origins

    def validate_token(self, token: str, valid_tokens: list[str]) -> bool:
        if not valid_tokens:
            return bool(token)
        return token in valid_tokens

    async def authenticate_token(self, token: str) -> dict[str, Any]:
        if self._authenticator:
            result = await self._authenticator.validate_token(token)
            if result.get("valid"):
                return {"authenticated": True, "user_id": result.get("user_id", "")}
        return {"authenticated": False, "error": "Authentication required"}


class WSAuthenticator:
    """WebSocket connection authentication and security."""

    def __init__(self, authenticator: IAPIAuthenticator | None = None, logger: APILogger | None = None) -> None:
        self._authenticator = authenticator
        self._logger = logger or APILogger("ws.security")
        self._allowed_origins: list[str] = []
        self._rate_limits: dict[str, list[float]] = {}
        self._max_connections_per_ip: int = 50

    def allow_origin(self, origin: str) -> None:
        if origin not in self._allowed_origins:
            self._allowed_origins.append(origin)

    def set_max_connections_per_ip(self, limit: int) -> None:
        self._max_connections_per_ip = limit

    async def authenticate_connection(self, scope: dict[str, Any]) -> dict[str, Any]:
        headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
        query_string = scope.get("query_string", b"").decode("utf-8", errors="replace")

        token = ""
        auth_header = headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        if not token and "token" in query_string:
            from urllib.parse import parse_qs
            token = parse_qs(query_string).get("token", [""])[0]

        if self._authenticator and token:
            result = await self._authenticator.validate_token(token)
            if result.get("valid"):
                return {"authenticated": True, "user_id": result.get("user_id", ""), "token": token}
        return {"authenticated": False, "error": "Authentication required"}

    def validate_origin(self, origin: str) -> bool:
        if not self._allowed_origins:
            return True
        return any(origin == allowed or origin.endswith(f"://{allowed}") for allowed in self._allowed_origins)

    def check_rate_limit(self, key: str, max_attempts: int = 10, window_sec: int = 60) -> bool:
        now = time.time()
        if key not in self._rate_limits:
            self._rate_limits[key] = []
        self._rate_limits[key] = [t for t in self._rate_limits[key] if now - t < window_sec]
        if len(self._rate_limits[key]) >= max_attempts:
            return False
        self._rate_limits[key].append(now)
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "authenticator_configured": self._authenticator is not None,
            "allowed_origins": list(self._allowed_origins),
            "max_connections_per_ip": self._max_connections_per_ip,
        }
