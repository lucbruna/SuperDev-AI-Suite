from __future__ import annotations

import logging
from typing import Any


class IntegrationAuth:
    """Authentication handling for integrations."""

    def __init__(self) -> None:
        self._credentials: dict[str, dict[str, Any]] = {}
        self._log = logging.getLogger("superdev.workflow.integrations.auth")

    def store(self, integration_id: str, credentials: dict[str, Any]) -> None:
        self._credentials[integration_id] = credentials

    def get(self, integration_id: str) -> dict[str, Any] | None:
        return self._credentials.get(integration_id)
