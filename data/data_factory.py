from __future__ import annotations

from typing import Any

from .data_config import DataConfig
from .data_engine import DataEngine
from .data_manager import DataManager


class DataFactory:
    """Factory for creating Data & Analytics components from config."""

    @staticmethod
    def create_engine(config: DataConfig | None = None) -> DataEngine:
        return DataEngine(config=config or DataConfig.default())

    @staticmethod
    def create_manager(config: DataConfig | None = None) -> DataManager:
        return DataManager(config=config or DataConfig.default())

    @staticmethod
    def from_dict(data: dict[str, Any]) -> DataConfig:
        return DataConfig(**{
            k: v for k, v in data.items()
            if k in DataConfig.__dataclass_fields__
        })


__all__ = ["DataFactory"]
