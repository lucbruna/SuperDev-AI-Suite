from __future__ import annotations

from typing import Any, Callable


class KeyboardNavigation:
    """Registers and dispatches keyboard shortcuts."""

    def __init__(self) -> None:
        self._shortcuts: dict[str, Callable[[], None]] = {}

    def register(self, shortcut: str, handler: Callable[[], None], description: str = "") -> None:
        self._shortcuts[shortcut] = handler

    def unregister(self, shortcut: str) -> bool:
        return self._shortcuts.pop(shortcut, None) is not None

    def handle(self, key: str, modifiers: dict[str, bool] | None = None) -> bool:
        modifiers = modifiers or {}
        parts = []
        if modifiers.get("ctrl"):
            parts.append("ctrl")
        if modifiers.get("shift"):
            parts.append("shift")
        if modifiers.get("alt"):
            parts.append("alt")
        parts.append(key.lower())
        combo = "+".join(parts)
        handler = self._shortcuts.get(combo)
        if handler is None:
            return False
        handler()
        return True

    def registered(self) -> list[dict[str, Any]]:
        return [
            {"shortcut": combo, "handler": handler.__name__}
            for combo, handler in self._shortcuts.items()
        ]
