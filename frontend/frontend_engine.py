from __future__ import annotations

import logging
from typing import Any

from .frontend_context import FrontendContext
from .frontend_manager import FrontendManager
from .frontend_registry import FrontendRegistry


class FrontendEngine:
    """Orchestrates the full SuperDev frontend experience."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend")
        self._context = context or FrontendContext()
        self._registry = FrontendRegistry()
        self._manager = FrontendManager(context=self._context)
        self._config: dict[str, Any] = {}
        self._running = False
        self._initialized = False

    def initialize(self, config: dict[str, Any] | None = None) -> dict[str, Any]:
        if config:
            self._config.update(config)
        self._initialized = True
        return {"initialized": True, "routes": len(self._registry.list_routes())}

    def start(self) -> dict[str, Any]:
        self._running = True
        return {"status": "running"}

    def shutdown(self) -> bool:
        self._running = False
        return True

    def render(self, route: str, **kwargs: Any) -> dict[str, Any]:
        resolved = self._registry.resolve_route(route)
        if resolved is None:
            return {"route": route, "status": "not_found"}
        screen = resolved["handler"]
        name = getattr(screen, "__name__", str(screen))
        result = self._manager.activate(name, **kwargs)
        return {"route": route, "status": "ok", **result}

    def navigate(self, route: str, **kwargs: Any) -> dict[str, Any]:
        result = self.render(route, **kwargs)
        self._context.active_route = route
        return result

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "running": self._running,
            "routes": len(self._registry.list_routes()),
            "screens": len(self._manager.list_screens()),
            "platform": self._context.platform,
            "theme": self._context.theme,
        }
