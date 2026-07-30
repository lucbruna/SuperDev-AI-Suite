from __future__ import annotations

import logging
import time
from typing import Any


class IntegrationLogger:
    """Logs integration activity."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._log = logging.getLogger("superdev.workflow.integrations.logger")

    def log(self, integration_id: str, action: str, status: str, details: dict[str, Any] | None = None) -> None:
        entry = {
            "integration_id": integration_id,
            "action": action,
            "status": status,
            "timestamp": time.time(),
            "details": details or {},
        }
        self._entries.append(entry)
        self._log.debug("Integration %s: %s -> %s", integration_id, action, status)

    def get_history(self, integration_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e["integration_id"] == integration_id]
