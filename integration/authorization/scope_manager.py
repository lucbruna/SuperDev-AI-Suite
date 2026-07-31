from __future__ import annotations

import logging
from typing import Any

from .role_mapping import RoleMapper


class ScopeManager:
    """Manages OAuth-style scopes and checks scope membership."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.authorization.scopes")
        self._registered: dict[str, str] = {}  # scope -> description

    def register(self, scope: str, description: str = "") -> None:
        self._registered[scope] = description

    def check(self, granted: list[str], required: str) -> bool:
        """Returns True when a granted scope satisfies a required scope.
        Supports hierarchical scopes: granting 'connections:*' satisfies
        'connections:connect'.
        """
        if required in granted:
            return True
        prefix = required.split(":")[0]
        return f"{prefix}:*" in granted

    def check_any(self, granted: list[str], required: list[str]) -> bool:
        return any(self.check(granted, req) for req in required)

    def require(self, granted: list[str], required: str) -> None:
        if not self.check(granted, required):
            raise PermissionError(f"missing required scope {required!r}")

    def list(self) -> list[str]:
        return sorted(self._registered)

    def snapshot(self) -> dict[str, int]:
        return {"scopes": len(self._registered)}
