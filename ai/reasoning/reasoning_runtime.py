from __future__ import annotations

from typing import Any

from .reasoning_config import ReasoningConfig
from .reasoning_logger import ReasoningLogger
from .reasoning_metrics import ReasoningMetrics


class ReasoningRuntime:
    """Runtime environment for reasoning execution."""

    def __init__(self, config: ReasoningConfig | None = None):
        self.config = config or ReasoningConfig()
        self.logger = ReasoningLogger()
        self.metrics = ReasoningMetrics()
        self._started = False

    async def start(self) -> None:
        self._started = True
        self.logger.info("Reasoning runtime started", config=self.config.to_dict())

    async def stop(self) -> None:
        self._started = False
        self.logger.info("Reasoning runtime stopped")

    @property
    def is_running(self) -> bool:
        return self._started

    def status(self) -> dict[str, Any]:
        return {
            "running": self._started,
            "config": self.config.to_dict(),
            "metrics": self.metrics.snapshot(),
        }
