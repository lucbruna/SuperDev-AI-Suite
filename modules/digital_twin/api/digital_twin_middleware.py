"""Middleware for the Digital Twin API: permission checks and logging."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from modules.digital_twin.api.digital_twin_responses import ApiResponse
from modules.digital_twin.config.permissions import Permissions

MiddlewareFn = Callable[[str, str, dict[str, object]], ApiResponse | None]


@dataclass(slots=True)
class MiddlewareChain:
    """Runs middleware in order; first rejection short-circuits."""

    middlewares: list[MiddlewareFn] = field(default_factory=list)

    def add(self, middleware: MiddlewareFn) -> None:
        self.middlewares.append(middleware)

    def run(self, endpoint: str, role: str, params: dict[str, object]) -> ApiResponse | None:
        for middleware in self.middlewares:
            rejection = middleware(endpoint, role, params)
            if rejection is not None:
                return rejection
        return None


def permission_middleware(permissions: Permissions) -> MiddlewareFn:
    """Reject the call when the route's permission is not granted."""

    def check(endpoint: str, role: str, params: dict[str, object]) -> ApiResponse | None:
        required = params.get("_permission")
        if required and not permissions.can(str(required)):
            return ApiResponse.forbidden(f"permission required: {required}")
        return None

    return check


def audit_middleware(audit_log: list[dict[str, object]]) -> MiddlewareFn:
    """Record every allowed call into the given audit log."""

    def audit(endpoint: str, role: str, params: dict[str, object]) -> ApiResponse | None:
        audit_log.append({"endpoint": endpoint, "role": role})
        return None

    return audit
