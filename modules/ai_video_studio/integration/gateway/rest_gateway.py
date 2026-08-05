"""REST Gateway — in-memory route registration for REST APIs."""
from __future__ import annotations

from typing import Any


class RESTGateway:
    """Registers REST routes and exposes them for introspection."""

    def __init__(self) -> None:
        self._routes: dict[str, dict[str, Any]] = {}

    def register(self, method: str, path: str, *, handler: str = "studio") -> dict[str, Any]:
        key = f"{method.upper()} {path}"
        self._routes[key] = {"method": method.upper(), "path": path, "handler": handler}
        return {"registered": key}

    def routes(self) -> dict[str, Any]:
        return {"routes": list(self._routes.values()), "count": len(self._routes)}


_rest_gateway: RESTGateway | None = None


def get_rest_gateway() -> RESTGateway:
    global _rest_gateway
    if _rest_gateway is None:
        _rest_gateway = RESTGateway()
    return _rest_gateway
