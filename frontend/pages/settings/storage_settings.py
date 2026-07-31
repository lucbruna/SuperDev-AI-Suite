from __future__ import annotations

import logging
from typing import Any


class StorageSettings:
    """Storage usage and provider selection."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.settings.storage")
        self._providers: list[dict[str, Any]] = [
            {"provider_id": "local", "name": "Local"},
            {"provider_id": "s3", "name": "Amazon S3"},
            {"provider_id": "gcs", "name": "Google Cloud Storage"},
        ]
        self._current = "local"

    def render(self) -> dict[str, Any]:
        return {"usage": self.usage(), "providers": self.providers(), "current": self._current}

    def usage(self) -> dict[str, Any]:
        return {"used_gb": 24.5, "quota_gb": 500, "percent": 4.9}

    def providers(self) -> list[dict[str, Any]]:
        return list(self._providers)

    def set_provider(self, provider_id: str) -> bool:
        if provider_id not in {p["provider_id"] for p in self._providers}:
            return False
        self._current = provider_id
        return True
