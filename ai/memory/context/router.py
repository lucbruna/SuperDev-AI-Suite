from __future__ import annotations

from typing import Any


class ContextRouter:
    """Routes context data to appropriate handlers based on type or rules."""

    def __init__(self):
        self._routes: dict[str, Any] = {}
        self._route_count: int = 0

    @property
    def route_count(self) -> int:
        return self._route_count

    def register_route(self, route_key: str, handler: Any) -> None:
        self._routes[route_key] = handler

    def unregister_route(self, route_key: str) -> bool:
        return self._routes.pop(route_key, None) is not None

    def route(self, context: dict[str, Any], route_key: str | None = None) -> Any:
        key = route_key or context.get("type", context.get("metadata", {}).get("type", "default"))
        handler = self._routes.get(key)
        if handler is None:
            raise KeyError(f"No handler registered for route: {key}")
        self._route_count += 1
        return handler(context)

    def route_by_source(self, context: dict[str, Any]) -> Any:
        sources = context.get("sources", [])
        for src in sources:
            handler = self._routes.get(src)
            if handler:
                self._route_count += 1
                return handler(context)
        handler = self._routes.get("default")
        if handler is None:
            raise KeyError(f"No handler found for sources: {sources}")
        self._route_count += 1
        return handler(context)

    def list_routes(self) -> list[str]:
        return list(self._routes.keys())

    def clear_routes(self) -> None:
        self._routes.clear()

    def reset(self) -> None:
        self._routes.clear()
        self._route_count = 0
