from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cloud_engine import CloudEngine


class CostManager:
    """Estimates and tracks cloud costs across providers."""

    def __init__(self, engine: CloudEngine) -> None:
        self._log = logging.getLogger("superdev.devops.cloud.costs")
        self._engine = engine

    def estimate(self, provider: str, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def get_usage(self, provider: str, period: str = "month") -> dict[str, Any]:
        raise NotImplementedError

    def forecast(self, provider: str, horizon_days: int = 30) -> dict[str, Any]:
        raise NotImplementedError

    def optimize(self, provider: str) -> list[dict[str, Any]]:
        raise NotImplementedError
