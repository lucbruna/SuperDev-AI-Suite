from __future__ import annotations

from typing import Any

from ..api_constants import CORS_ALLOW_HEADERS, CORS_ALLOW_METHODS, CORS_DEFAULT_ORIGINS, CORS_EXPOSE_HEADERS
from ..api_interfaces import IAPIMiddleware
from ..api_models import APIResponse


class CORSMiddleware(IAPIMiddleware):
    """CORS middleware for cross-origin requests."""

    def __init__(
        self,
        allowed_origins: list[str] | None = None,
        allowed_methods: list[str] | None = None,
        allowed_headers: list[str] | None = None,
        expose_headers: list[str] | None = None,
        allow_credentials: bool = True,
        max_age: int = 3600,
    ) -> None:
        if "*" in (allowed_origins or list(CORS_DEFAULT_ORIGINS)) and allow_credentials:
            raise ValueError(
                "CORS: wildcard origin with allow_credentials=True is forbidden")
        self._allowed_origins = allowed_origins or list(CORS_DEFAULT_ORIGINS)
        self._allowed_methods = allowed_methods or list(CORS_ALLOW_METHODS)
        self._allowed_headers = allowed_headers or list(CORS_ALLOW_HEADERS)
        self._expose_headers = expose_headers or list(CORS_EXPOSE_HEADERS)
        self._allow_credentials = allow_credentials
        self._max_age = max_age

    def _origin_allowed(self, origin: str) -> str:
        if "*" in self._allowed_origins:
            return "*"
        if origin in self._allowed_origins:
            return origin
        return ""

    def is_origin_allowed(self, origin: str) -> bool:
        return self._origin_allowed(origin) != ""

    async def before_request(self, request: Any) -> Any:
        headers = getattr(request, "headers", {})
        origin = headers.get("origin", "") if isinstance(headers, dict) else ""
        method = getattr(request, "method", "GET")

        if method == "OPTIONS" and isinstance(headers, dict):
            requested_method = headers.get("access-control-request-method", "")
            if requested_method and requested_method.upper() not in self._allowed_methods:
                return APIResponse(status_code=403, body="CORS: Method not allowed")

            allowed_origin = self._origin_allowed(origin)
            if not allowed_origin:
                return APIResponse(status_code=403, body="CORS: Origin not allowed")

            response_headers = {
                "access-control-allow-origin": allowed_origin,
                "access-control-allow-methods": ", ".join(self._allowed_methods),
                "access-control-allow-headers": ", ".join(self._allowed_headers),
                "access-control-max-age": str(self._max_age),
            }
            if self._allow_credentials:
                response_headers["access-control-allow-credentials"] = "true"
            if self._expose_headers:
                response_headers["access-control-expose-headers"] = ", ".join(self._expose_headers)

            return APIResponse(status_code=204, body="", headers=response_headers)

        return None

    async def after_request(self, response: Any) -> Any:
        origin = ""
        if hasattr(response, "_context") and hasattr(response._context, "request"):
            req_headers = getattr(response._context.request, "headers", {})
            origin = req_headers.get("origin", "") if isinstance(req_headers, dict) else ""

        if hasattr(response, "headers") and isinstance(response.headers, dict):
            allowed_origin = self._origin_allowed(origin)
            response.headers.setdefault("access-control-allow-origin", allowed_origin)
            if self._allow_credentials:
                response.headers.setdefault("access-control-allow-credentials", "true")
            if self._expose_headers:
                response.headers.setdefault("access-control-expose-headers", ", ".join(self._expose_headers))

        return response

    def to_dict(self) -> dict[str, Any]:
        return {
            "middleware": "CORSMiddleware",
            "allowed_origins": self._allowed_origins,
            "allow_credentials": self._allow_credentials,
        }
