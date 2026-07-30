from __future__ import annotations

import logging
from typing import Any


class CodeRuntime:
    """Runtime context for active code sessions."""

    def __init__(self) -> None:
        self._active: dict[str, dict[str, Any]] = {}
        self._log = logging.getLogger("superdev.code.runtime")

    def start(self, session_id: str) -> None:
        self._active[session_id] = {"status": "running"}
        self._log.info("Runtime started for session %s", session_id)

    def stop(self, session_id: str) -> None:
        self._active.pop(session_id, None)

    def is_running(self, session_id: str) -> bool:
        return session_id in self._active
