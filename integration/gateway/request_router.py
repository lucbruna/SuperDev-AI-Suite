from __future__ import annotations

import logging
from typing import Any, Callable


class RequestRouter:
    """Routes inbound requests to registered handlers by method+path."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.gateway.router")
        self._handlers: dict[str, Callable[..., Any]] = {}

    def _key(self, method: str, path: str) -> str:
        return f"{method.upper()} {path}"

    def register(self, method: str, path: str, handler: Callable[..., Any]) -> None:
        self._handlers[self._key(method, path)] = handler

    def unregister(self, method: str, path: str) -> bool:
        return self._handlers.pop(self._key(method, path), None) is not None

    def get_handler(self, method: str, path: str) -> Callable[..., Any] | None:
        return self._handlers.get(self._key(method, path))

    def has(self, method: str, path: str) -> bool:
        return self._key(method, path) in self._handlers

    def dispatch(self, method: str, path: str, params: dict[str, Any] | None = None) -> Any:
        handler = self.get_handler(method, path)
        if handler is None:
            raise KeyError(f"no handler for {method.upper()} {path}")
        return handler(params or {})

    def routes(self) -> list[str]:
        return sorted(self._handlers)
