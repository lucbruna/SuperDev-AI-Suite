from __future__ import annotations

from typing import Any

from ..api_interfaces import IAPIRouter
from ..api_models import HTTPMethod


class RESTRouter(IAPIRouter):
    """Protocol-specific router for REST endpoints."""

    def __init__(self) -> None:
        self._routes: list[dict[str, Any]] = []
        self._registered = False

    def add_route(
        self,
        method: str | HTTPMethod,
        path: str,
        handler: Any,
        **metadata: Any,
    ) -> None:
        method_str = method.value if isinstance(method, HTTPMethod) else method.upper()
        self._routes.append({
            "method": method_str,
            "path": path,
            "handler": handler,
            **metadata,
        })

    def get(self, path: str, handler: Any, **metadata: Any) -> None:
        self.add_route(HTTPMethod.GET, path, handler, **metadata)

    def post(self, path: str, handler: Any, **metadata: Any) -> None:
        self.add_route(HTTPMethod.POST, path, handler, **metadata)

    def put(self, path: str, handler: Any, **metadata: Any) -> None:
        self.add_route(HTTPMethod.PUT, path, handler, **metadata)

    def patch(self, path: str, handler: Any, **metadata: Any) -> None:
        self.add_route(HTTPMethod.PATCH, path, handler, **metadata)

    def delete(self, path: str, handler: Any, **metadata: Any) -> None:
        self.add_route(HTTPMethod.DELETE, path, handler, **metadata)

    def register_routes(self, app: Any) -> None:
        registry = getattr(app, "registry", None)
        if registry is None or not hasattr(registry, "register_route"):
            return
        for route in self._routes:
            registry.register_route(
                route["method"],
                route["path"],
                route["handler"],
                auth_required=route.get("auth_required", True),
                description=route.get("description", ""),
                tags=route.get("tags", []),
            )
        self._registered = True

    def get_routes(self) -> dict[str, Any]:
        return {r["method"] + ":" + r["path"]: r for r in self._routes}

    def to_dict(self) -> dict[str, Any]:
        return {
            "routes": len(self._routes),
            "registered": self._registered,
            "route_list": [
                {"method": r["method"], "path": r["path"]}
                for r in self._routes
            ],
        }
