from __future__ import annotations

import logging
from typing import Any, Callable


class WebMiddleware:
    """Middleware pipeline for the web application."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.web.middleware")
        self._middlewares: list[Any] = []

    def use(self, middleware: Any) -> None:
        self._middlewares.append(middleware)

    def run(self, request: dict[str, Any], handler: Callable[..., Any]) -> dict[str, Any]:
        for middleware in self._middlewares:
            middleware(request)
        return handler(request)

    def list(self) -> list[str]:
        return [m.__class__.__name__ for m in self._middlewares]

    def clear(self) -> None:
        self._middlewares.clear()
