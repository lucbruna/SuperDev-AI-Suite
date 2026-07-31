from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cloud_engine import CloudEngine


class ResourceManager:
    """Manages cloud resources across providers."""

    def __init__(self, engine: CloudEngine) -> None:
        self._log = logging.getLogger("superdev.devops.cloud.resources")
        self._engine = engine

    def create(self, provider: str, resource_type: str, name: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def delete(self, provider: str, resource_id: str) -> bool:
        raise NotImplementedError

    def list(self, provider: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def get(self, provider: str, resource_id: str) -> dict[str, Any]:
        raise NotImplementedError

    def tag(self, provider: str, resource_id: str, tags: dict[str, str]) -> bool:
        raise NotImplementedError
