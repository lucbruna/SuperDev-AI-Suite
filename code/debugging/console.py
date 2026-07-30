from __future__ import annotations

import logging


class DebugConsole:
    """Interactive debug console for evaluating expressions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.debugging.console")
        self._history: list[str] = []

    def execute(self, command: str) -> str:
        self._history.append(command)
        self._log.debug("Executing: %s", command)
        return ""

    @property
    def history(self) -> list[str]:
        return list(self._history)
