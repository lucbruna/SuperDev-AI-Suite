from __future__ import annotations

from typing import Any

from .data_config import DataConfig
from .data_engine import DataEngine
from .data_registry import DataRegistry


class DataManager:
    """High-level lifecycle manager for the Data & Analytics Engine."""

    def __init__(self, config: DataConfig | None = None) -> None:
        self._config = config or DataConfig.default()
        self._engine: DataEngine | None = None
        self._registry = DataRegistry()

    async def initialize(self) -> DataEngine:
        engine = DataEngine(config=self._config)
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

    def get_engine(self) -> DataEngine:
        if self._engine is None:
            raise RuntimeError("Engine not initialized")
        return self._engine

    @property
    def registry(self) -> DataRegistry:
        return self._registry

    @property
    def config(self) -> DataConfig:
        return self._config

    def status(self) -> dict[str, Any]:
        if self._engine is None:
            return {"initialized": False}
        return {"initialized": True, "engine": self._engine.status()}


__all__ = ["DataManager"]
