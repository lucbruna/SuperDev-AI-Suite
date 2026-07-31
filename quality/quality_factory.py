from __future__ import annotations

from typing import Any

from .quality_config import QualityConfig
from .quality_engine import QualityEngine
from .quality_manager import QualityManager


class QualityFactory:
    """Factory for creating Testing & Quality components from config."""

    @staticmethod
    def create_engine(config: QualityConfig | None = None) -> QualityEngine:
        return QualityEngine(config=config or QualityConfig.default())

    @staticmethod
    def create_manager(config: QualityConfig | None = None) -> QualityManager:
        return QualityManager(config=config or QualityConfig.default())

    @staticmethod
    def from_dict(data: dict[str, Any]) -> QualityConfig:
        return QualityConfig(**{
            k: v for k, v in data.items()
            if k in QualityConfig.__dataclass_fields__
        })


__all__ = ["QualityFactory"]
