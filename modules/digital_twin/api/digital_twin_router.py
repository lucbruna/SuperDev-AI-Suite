"""Router: dispatch endpoint calls through middleware to handlers."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.api.digital_twin_endpoints import ENDPOINT_ENDPOINTS
from modules.digital_twin.api.digital_twin_handlers import HandlerFn
from modules.digital_twin.api.digital_twin_middleware import (
    MiddlewareChain,
    permission_middleware,
)
from modules.digital_twin.api.digital_twin_responses import ApiResponse
from modules.digital_twin.api.digital_twin_routes import ROUTE_BY_NAME, permission_for
from modules.digital_twin.config.permissions import Permissions


@dataclass(slots=True)
class TwinRouter:
    """Dispatches ``(endpoint, params, role)`` to the right handler."""

    handlers: dict[str, HandlerFn] = field(default_factory=dict)
    middleware: MiddlewareChain = field(default_factory=MiddlewareChain)
    permissions: Permissions | None = None

    def __post_init__(self) -> None:
        if self.permissions is not None:
            self.middleware.add(permission_middleware(self.permissions))

    def register(self, name: str, handler: HandlerFn) -> None:
        self.handlers[name] = handler

    def endpoint_names(self) -> list[str]:
        return sorted(self.handlers)

    def dispatch(
        self,
        endpoint: str,
        params: dict[str, object] | None = None,
        *,
        role: str = "admin",
    ) -> ApiResponse:
        params = dict(params or {})
        if endpoint == ENDPOINT_ENDPOINTS:
            return ApiResponse.success({"endpoints": self.endpoint_names()})
        if endpoint not in ROUTE_BY_NAME:
            return ApiResponse.not_found(f"endpoint not found: {endpoint}")
        if endpoint not in self.handlers:
            return ApiResponse.not_found(f"no handler for endpoint: {endpoint}")

        params["_permission"] = permission_for(endpoint)
        rejection = self.middleware.run(endpoint, role, params)
        if rejection is not None:
            return rejection
        params.pop("_permission", None)

        handler = self.handlers[endpoint]
        try:
            return handler(**params)
        except TypeError as exc:
            return ApiResponse.failure(f"invalid parameters: {exc}")
        except Exception as exc:  # noqa: BLE001 - API boundary
            return ApiResponse.internal(str(exc))
