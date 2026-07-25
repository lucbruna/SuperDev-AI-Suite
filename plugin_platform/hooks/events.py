from __future__ import annotations

from typing import Any


class PluginEventHook:
    def __init__(self) -> None:
        self._before_handlers: list[Any] = []
        self._after_handlers: list[Any] = []
        self._error_handlers: list[Any] = []

    def before_execution(self, context: dict[str, Any], params: dict[str, Any]) -> None:
        for handler in self._before_handlers:
            handler(context, params)

    def after_execution(self, context: dict[str, Any], result: Any) -> None:
        for handler in self._after_handlers:
            handler(context, result)

    def on_error(self, context: dict[str, Any], error: Exception) -> None:
        for handler in self._error_handlers:
            handler(context, error)

    def add_before_handler(self, handler: Any) -> None:
        self._before_handlers.append(handler)

    def add_after_handler(self, handler: Any) -> None:
        self._after_handlers.append(handler)

    def add_error_handler(self, handler: Any) -> None:
        self._error_handlers.append(handler)

    def remove_before_handler(self, handler: Any) -> None:
        if handler in self._before_handlers:
            self._before_handlers.remove(handler)

    def remove_after_handler(self, handler: Any) -> None:
        if handler in self._after_handlers:
            self._after_handlers.remove(handler)

    def remove_error_handler(self, handler: Any) -> None:
        if handler in self._error_handlers:
            self._error_handlers.remove(handler)