from __future__ import annotations

import logging
from typing import Any


class IntegrationHttp:
    """HTTP client for integration calls."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.integrations.http")

    def get(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        self._log.info("GET %s", url)
        return {"status": "ok", "url": url}

    def post(self, url: str, data: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        self._log.info("POST %s", url)
        return {"status": "ok", "url": url}
