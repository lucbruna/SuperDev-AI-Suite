from __future__ import annotations

from typing import Any

from .api_interfaces import IAPIRouter


class APIRegistry:
    """Central registry for API routes, handlers, and services."""

    def __init__(self) -> None:
        self._routes: dict[str, dict[str, Any]] = {}
        self._handlers: dict[str, Any] = {}
        self._services: dict[str, Any] = {}
        self._middleware: list[Any] = []

    def register_route(self, method: str, path: str, handler: Any, **metadata: Any) -> str:
        key = f"{method.upper()}:{path}"
        self._routes[key] = {"method": method.upper(), "path": path, "handler": handler, **metadata}
        return key

    def register_handler(self, name: str, handler: Any) -> str:
        self._handlers[name] = handler
        return name

    def register_service(self, name: str, service: Any) -> str:
        self._services[name] = service
        return name

    def register_middleware(self, middleware: Any) -> None:
        self._middleware.append(middleware)

    def get_route(self, method: str, path: str) -> dict[str, Any] | None:
        return self._routes.get(f"{method.upper()}:{path}")

    def get_handler(self, name: str) -> Any:
        return self._handlers.get(name)

    def get_service(self, name: str) -> Any:
        return self._services.get(name)

    def get_routes(self) -> dict[str, dict[str, Any]]:
        return dict(self._routes)

    def list_routes(self) -> list[dict[str, Any]]:
        return list(self._routes.values())

    def list_handlers(self) -> list[str]:
        return list(self._handlers.keys())

    def list_services(self) -> list[str]:
        return list(self._services.keys())

    def to_dict(self) -> dict[str, Any]:
        return {
            "routes": len(self._routes),
            "handlers": len(self._handlers),
            "services": len(self._services),
            "middleware": len(self._middleware),
        }
