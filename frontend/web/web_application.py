from __future__ import annotations

import logging
from typing import Any

from ..frontend_config import FrontendConfig
from ..frontend_context import FrontendContext
from .routes.web_routes import WebRoutes


class WebApplication:
    """Main web application."""

    def __init__(self, config: FrontendConfig | None = None, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.web")
        self._config = config or FrontendConfig()
        self._context = context or FrontendContext(platform="web")
        self._routes = WebRoutes()
        self._middlewares: list[Any] = []
        self._started = False

    def start(self, host: str = "0.0.0.0", port: int = 8000, **kwargs: Any) -> dict[str, Any]:
        self._started = True
        self._log.info("web application started on %s:%s", host, port)
        return {"status": "started", "host": host, "port": port}

    def stop(self) -> bool:
        self._started = False
        return True

    def serve(self) -> None:
        self._log.info("web server ready on %s", self._config.base_url)

    def handle_request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        request: dict[str, Any] = {"method": method, "path": path, **kwargs}
        for middleware in self._middlewares:
            middleware(request)
        resolved = self._routes.resolve(method, path)
        return {
            "method": method,
            "path": path,
            "status": "ok" if resolved["matched"] else "not_found",
            "handler": resolved["handler"],
        }

    def register_middleware(self, middleware: Any) -> None:
        self._middlewares.append(middleware)

    def status(self) -> dict[str, Any]:
        return {
            "started": self._started,
            "routes": len(self._routes.list()),
            "middlewares": len(self._middlewares),
            "base_url": self._config.base_url,
        }
