from __future__ import annotations

import logging
from typing import Any


class VariableInspector:
    """Inspects variables during debugging sessions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.debugging.variables")

    def get_value(self, name: str) -> Any | None:
        self._log.debug("Inspecting variable %s", name)
        return None

    def list_locals(self) -> dict[str, Any]:
        return {}

    def list_globals(self) -> dict[str, Any]:
        return {}
