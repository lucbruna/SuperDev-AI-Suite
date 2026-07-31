from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cloud_engine import CloudEngine


class RegionManager:
    """Manages cloud regions and availability zones."""

    def __init__(self, engine: CloudEngine) -> None:
        self._log = logging.getLogger("superdev.devops.cloud.regions")
        self._engine = engine

    def list(self, provider: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def zones(self, provider: str, region: str) -> list[str]:
        raise NotImplementedError

    def select(self, provider: str, criteria: dict[str, Any]) -> str:
        raise NotImplementedError

    def latency(self, provider: str, region: str) -> int:
        raise NotImplementedError
