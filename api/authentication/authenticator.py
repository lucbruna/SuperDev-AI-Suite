from __future__ import annotations

from typing import Any

from ..api_events import APIEventBus, APIEventType
from ..api_interfaces import IAPIAuthenticator
from ..api_logger import APILogger
from ..api_metrics import APIMetrics


class Authenticator(IAPIAuthenticator):
    """Main authenticator that delegates to registered auth handlers."""

    def __init__(
        self,
        logger: APILogger | None = None,
        metrics: APIMetrics | None = None,
        events: APIEventBus | None = None,
    ) -> None:
        self._logger = logger or APILogger("auth.authenticator")
        self._metrics = metrics
        self._events = events
        self._handlers: dict[str, IAPIAuthenticator] = {}
        self._token_prefix_map: dict[str, str] = {}

    def register_handler(self, scheme: str, handler: IAPIAuthenticator) -> None:
        self._handlers[scheme] = handler

    def register_token_prefix(self, prefix: str, scheme: str) -> None:
        self._token_prefix_map[prefix] = scheme

    async def authenticate(self, request: Any) -> dict[str, Any]:
        headers = getattr(request, "headers", request if isinstance(request, dict) else {})
        auth_header = ""
        api_key = ""

        if isinstance(headers, dict):
            auth_header = headers.get("authorization", headers.get("Authorization", ""))
            api_key = headers.get("x-api-key", headers.get("X-API-Key", ""))

        token = ""
        scheme = "bearer"

        if api_key:
            token = api_key
            handler = self._handlers.get("apikey")
            if handler:
                result = await handler.authenticate({"headers": {"X-API-Key": api_key}})
                await self._emit_auth_event(result)
                return result

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            scheme = "bearer"
        elif auth_header.startswith("Basic "):
            import base64
            token = auth_header[6:]
            scheme = "basic"
            try:
                decoded = base64.b64decode(token).decode("utf-8")
                return {"authenticated": True, "method": "basic", "user": decoded.split(":")[0]}
            except Exception:
                return {"authenticated": False, "method": "basic", "error": "Invalid basic auth"}

        if token:
            for prefix, handler_scheme in self._token_prefix_map.items():
                if token.startswith(prefix):
                    scheme = handler_scheme
                    break

            handler = self._handlers.get(scheme)
            if handler:
                result = await handler.authenticate({"headers": {"Authorization": f"Bearer {token}"}})
                await self._emit_auth_event(result)
                return result

            return {"authenticated": False, "method": scheme, "error": "No handler for token type"}

        return {"authenticated": False, "method": "none", "error": "No credentials provided"}

    async def validate_token(self, token: str) -> dict[str, Any]:
        for scheme, handler in self._handlers.items():
            result = await handler.validate_token(token)
            if result.get("valid"):
                return result
        return {"valid": False, "error": "Token validation failed"}

    async def _emit_auth_event(self, result: dict[str, Any]) -> None:
        if self._events is None:
            return
        event_type = APIEventType.AUTH_SUCCESS if result.get("authenticated") else APIEventType.AUTH_FAILURE
        await self._events.emit(event_type, {"method": result.get("method", "unknown")})

    def to_dict(self) -> dict[str, Any]:
        return {
            "handlers": list(self._handlers.keys()),
            "token_prefixes": dict(self._token_prefix_map),
        }
