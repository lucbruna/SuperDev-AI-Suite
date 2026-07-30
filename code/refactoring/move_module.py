from __future__ import annotations

import logging


class MoveModule:
    """Moves modules between locations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.refactoring.move")

    def move(self, source: str, target: str) -> None:
        self._log.info("Moving %s -> %s", source, target)
