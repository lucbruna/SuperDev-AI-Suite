from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cloud_engine import CloudEngine


class AvailabilityManager:
    """Monitors and manages resource availability across providers."""

    def __init__(self, engine: CloudEngine) -> None:
        self._log = logging.getLogger("superdev.devops.cloud.availability")
        self._engine = engine

    def uptime(self, provider: str, resource_id: str) -> float:
        raise NotImplementedError

    def health(self, provider: str) -> dict[str, Any]:
        raise NotImplementedError

    def incidents(self, provider: str, days: int = 7) -> list[dict[str, Any]]:
        raise NotImplementedError

    def sla(self, provider: str) -> float:
        raise NotImplementedError
