"""Context for the DevOps & Cloud Infrastructure Engine (Volume 37)."""

from __future__ import annotations

import time
from typing import Any

from devops_engine.devops_config import DevopsConfig


class DevopsContext:
    """Operational context snapshot for the engine."""

    def __init__(self, config: DevopsConfig | None = None) -> None:
        self.config = config or DevopsConfig()
        self.tenant: str = "default"
        self.environment: str = self.config.env
        self.started_at: float = time.time()
        self.extra: dict[str, Any] = {}

    def snapshot(self) -> dict[str, Any]:
        return {
            "tenant": self.tenant,
            "environment": self.environment,
            "started_at": self.started_at,
            "extra": dict(self.extra),
        }
