from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ApplicationState:
    """Global application-level state."""

    initialized: bool = False
    boot_time: float = 0.0
    version: str = "5.0.0"
    features: dict[str, bool] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)

    def enable_feature(self, name: str) -> None:
        self.features[name] = True

    def disable_feature(self, name: str) -> None:
        self.features[name] = False

    def feature_enabled(self, name: str) -> bool:
        return self.features.get(name, False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "initialized": self.initialized,
            "boot_time": self.boot_time,
            "version": self.version,
            "features": dict(self.features),
            "config": dict(self.config),
        }
