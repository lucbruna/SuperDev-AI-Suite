from __future__ import annotations

from typing import Any


class PluginStartupHook:
    def __init__(self) -> None:
        self._startup_handlers: list[Any] = []
        self._shutdown_handlers: list[Any] = []

    def on_startup(self, context: dict[str, Any]) -> None:
        for handler in self._startup_handlers:
            handler(context)

    def on_shutdown(self, context: dict[str, Any]) -> None:
        for handler in self._shutdown_handlers:
            handler(context)

    def add_startup_handler(self, handler: Any) -> None:
        self._startup_handlers.append(handler)

    def add_shutdown_handler(self, handler: Any) -> None:
        self._shutdown_handlers.append(handler)

    def remove_startup_handler(self, handler: Any) -> None:
        if handler in self._startup_handlers:
            self._startup_handlers.remove(handler)

    def remove_shutdown_handler(self, handler: Any) -> None:
        if handler in self._shutdown_handlers:
            self._shutdown_handlers.remove(handler)