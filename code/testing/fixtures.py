from __future__ import annotations

import logging
from typing import Any


class FixtureManager:
    """Manages test fixtures lifecycle."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.testing.fixtures")
        self._fixtures: dict[str, Any] = {}

    def register(self, name: str, factory: Any, scope: str = "function") -> None:
        self._fixtures[name] = {"factory": factory, "scope": scope}
        self._log.debug("Registered fixture %s (scope=%s)", name, scope)

    def get(self, name: str) -> Any | None:
        fixture = self._fixtures.get(name)
        if fixture is None:
            return None
        return fixture["factory"]()

    def clear(self, scope: str | None = None) -> None:
        self._fixtures.clear()
