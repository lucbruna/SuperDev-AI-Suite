from __future__ import annotations

import logging
from typing import Any


class Debugger:
    """Main debugger for code execution."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.debugging")
        self._breakpoints: list[dict[str, Any]] = []
        self._stack: list[dict[str, Any]] = []

    def attach(self, target: str) -> None:
        self._log.info("Attaching to %s", target)

    def detach(self) -> None:
        self._log.info("Detaching debugger")

    def step_over(self) -> None:
        self._log.debug("Step over")

    def step_into(self) -> None:
        self._log.debug("Step into")

    def continue_execution(self) -> None:
        self._log.debug("Continue")

    @property
    def breakpoints(self) -> list[dict[str, Any]]:
        return list(self._breakpoints)
