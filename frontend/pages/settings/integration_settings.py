from __future__ import annotations

import logging
from typing import Any


class IntegrationSettings:
    """External integration connections."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.settings.integrations")
        self._connections: dict[str, bool] = {}

    def render(self) -> dict[str, Any]:
        return {"integrations": self.list(), "count": len(self._connections)}

    def list(self) -> list[dict[str, Any]]:
        return [
            {"integration_id": iid, "connected": connected}
            for iid, connected in self._connections.items()
        ]

    def connect(self, integration_id: str, credentials: dict[str, Any]) -> bool:
        if not credentials:
            return False
        self._connections[integration_id] = True
        return True

    def disconnect(self, integration_id: str) -> bool:
        return self._connections.pop(integration_id, None) is not None
