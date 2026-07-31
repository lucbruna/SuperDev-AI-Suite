from __future__ import annotations

import logging
from typing import Any


class FrontendRegistry:
    """Registry of frontend modules, routes, and components."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.registry")
        self._routes: dict[str, dict[str, Any]] = {}
        self._components: dict[str, Any] = {}
        self._plugins: dict[str, Any] = {}

    def register_route(self, path: str, handler: Any, **kwargs: Any) -> None:
        self._routes[path] = {"handler": handler, "kwargs": kwargs}

    def resolve_route(self, path: str) -> dict[str, Any]:
        if path in self._routes:
            return self._routes[path]
        segments = path.strip("/").split("/")
        for i in range(len(segments) - 1, 0, -1):
            candidate = "/" + "/".join(segments[:i])
            if candidate in self._routes:
                return self._routes[candidate]
        return None  # type: ignore[return-value]

    def register_component(self, name: str, component: Any) -> None:
        self._components[name] = component

    def get_component(self, name: str) -> Any:
        return self._components.get(name)

    def register_plugin(self, name: str, plugin: Any) -> None:
        self._plugins[name] = plugin

    def list_routes(self) -> list[str]:
        return sorted(self._routes)

    def list_components(self) -> list[str]:
        return sorted(self._components)

    def list_plugins(self) -> list[str]:
        return sorted(self._plugins)
