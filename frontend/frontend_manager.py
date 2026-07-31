from __future__ import annotations

import logging
from typing import Any

from .frontend_context import FrontendContext


class FrontendManager:
    """Manages frontend lifecycle, screens, and resources."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.manager")
        self._context = context or FrontendContext()
        self._screens: dict[str, Any] = {}
        self._active: str | None = None

    def register_screen(self, name: str, screen: Any) -> None:
        self._screens[name] = screen

    def unregister_screen(self, name: str) -> bool:
        return self._screens.pop(name, None) is not None

    def get_screen(self, name: str) -> Any:
        return self._screens.get(name)

    def list_screens(self) -> list[str]:
        return list(self._screens)

    def activate(self, name: str, **kwargs: Any) -> dict[str, Any]:
        if name not in self._screens:
            raise KeyError(f"screen not registered: {name}")
        self._active = name
        self._context.active_route = name
        return {"screen": name, "status": "active", "params": kwargs}
