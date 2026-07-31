from __future__ import annotations

import logging
from typing import Any


class WebRoutes:
    """Registers and resolves web application routes."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.web.routes")
        self._routes: dict[str, dict[str, Any]] = {}

    def add(self, path: str, handler: Any, methods: list[str] | None = None, **kwargs: Any) -> None:
        self._routes[path] = {"handler": handler, "methods": methods or ["GET"], "kwargs": kwargs}

    def resolve(self, method: str, path: str) -> dict[str, Any]:
        route = self._routes.get(path)
        if route is None:
            return {"path": path, "method": method, "handler": None, "matched": False}
        methods = route["methods"]
        matched = method in methods or "*" in methods
        return {"path": path, "method": method, "handler": route["handler"], "matched": matched}

    def list(self) -> list[dict[str, Any]]:
        return [
            {"path": path, "methods": route["methods"], "handler": route["handler"]}
            for path, route in self._routes.items()
        ]

    def remove(self, path: str) -> bool:
        return self._routes.pop(path, None) is not None
