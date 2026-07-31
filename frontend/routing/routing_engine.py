from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Route:
    """A registered route definition."""

    path: str
    name: str
    handler: Callable[..., Any]
    methods: list[str] = field(default_factory=lambda: ["GET"])
    requires_auth: bool = True
    permissions: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


class RoutingEngine:
    """Registers routes and resolves URLs to handlers."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.routing")
        self._routes: dict[str, Route] = {}
        self._history: list[str] = []
        self._current: str | None = None

    def add(self, path: str, name: str, handler: Callable[..., Any], **kwargs: Any) -> Route:
        route = Route(path=path, name=name, handler=handler, **kwargs)
        self._routes[name] = route
        return route

    def resolve(self, path: str) -> Route | None:
        for route in self._routes.values():
            if self._match(route.path, path):
                return route
        return None

    def get(self, name: str) -> Route | None:
        return self._routes.get(name)

    def navigate(self, path: str) -> str:
        self._history.append(path)
        self._current = path
        return path

    def back(self) -> str | None:
        if len(self._history) > 1:
            self._history.pop()
            self._current = self._history[-1]
            return self._current
        return None

    def current(self) -> str | None:
        return self._current

    def list(self) -> list[dict[str, Any]]:
        return [
            {"path": r.path, "name": r.name, "methods": list(r.methods), "requires_auth": r.requires_auth}
            for r in self._routes.values()
        ]

    def _match(self, pattern: str, path: str) -> bool:
        pattern_parts = pattern.strip("/").split("/")
        path_parts = path.strip("/").split("/")
        if len(pattern_parts) != len(path_parts):
            return False
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith(":") or pattern_part == "*":
                continue
            if pattern_part != path_part:
                return False
        return True
