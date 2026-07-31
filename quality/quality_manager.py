from __future__ import annotations

from typing import Any

from .quality_config import QualityConfig
from .quality_engine import QualityEngine
from .quality_registry import QualityRegistry


class QualityManager:
    """High-level lifecycle manager for the Testing & Quality Engine."""

    def __init__(self, config: QualityConfig | None = None) -> None:
        self._config = config or QualityConfig.default()
        self._engine: QualityEngine | None = None
        self._registry = QualityRegistry()

    async def initialize(self) -> QualityEngine:
        engine = QualityEngine(config=self._config)
        await engine.start()
        self._engine = engine
        return engine

    async def shutdown(self) -> None:
        if self._engine:
            await self._engine.stop()
            self._engine = None

    async def reload(self) -> None:
        await self.shutdown()
        await self.initialize()

    def get_engine(self) -> QualityEngine:
        if self._engine is None:
            raise RuntimeError("Engine not initialized")
        return self._engine

    @property
    def registry(self) -> QualityRegistry:
        return self._registry

    @property
    def config(self) -> QualityConfig:
        return self._config

    def status(self) -> dict[str, Any]:
        if self._engine is None:
            return {"initialized": False}
        return {"initialized": True, "engine": self._engine.status()}


__all__ = ["QualityManager"]
