from __future__ import annotations

from typing import Any, AsyncIterator

from .api_interfaces import IAPIRouter
from .api_registry import APIRegistry


class APIRouter(IAPIRouter):
    """Core router that delegates to protocol-specific routers."""

    def __init__(self, registry: APIRegistry) -> None:
        self._registry = registry
        self._protocol_routers: dict[str, IAPIRouter] = {}

    def register_protocol_router(self, protocol: str, router: IAPIRouter) -> None:
        self._protocol_routers[protocol] = router

    def register_routes(self, app: Any) -> None:
        for router in self._protocol_routers.values():
            router.register_routes(app)

    def get_routes(self) -> dict[str, Any]:
        routes: dict[str, Any] = {}
        for protocol, router in self._protocol_routers.items():
            routes[protocol] = router.get_routes()
        return routes

    def add_route(self, method: str, path: str, handler: Any, **metadata: Any) -> str:
        return self._registry.register_route(method, path, handler, **metadata)

    def get_protocol_router(self, protocol: str) -> IAPIRouter | None:
        return self._protocol_routers.get(protocol)

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocols": list(self._protocol_routers.keys()),
            "routes": self._registry.list_routes(),
        }
