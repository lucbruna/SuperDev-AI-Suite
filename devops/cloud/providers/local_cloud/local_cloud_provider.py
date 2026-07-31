from __future__ import annotations

import logging
from typing import Any

from ...interfaces import IDevOpsProvider


class LocalCloudProvider(IDevOpsProvider):
    """Local (docker-based) cloud provider for development and testing."""

    name = "local"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.cloud.providers.local")
        self._config = config or {}

    def connect(self, credentials: dict[str, Any]) -> bool:
        raise NotImplementedError

    def disconnect(self) -> bool:
        raise NotImplementedError

    def is_connected(self) -> bool:
        raise NotImplementedError

    def list_resources(self, resource_type: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def create_resource(self, resource_type: str, spec: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        raise NotImplementedError
