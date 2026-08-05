"""Process-wide settings singleton for the intelligence module."""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from modules.architecture_intelligence.config.intelligence_config import (
    IntelligenceConfig,
)

_settings: "IntelligenceSettings | None" = None
_lock = threading.Lock()


class IntelligenceSettings:
    """Lazy singleton that owns the resolved config and directories."""

    def __init__(self, config: IntelligenceConfig | None = None) -> None:
        self.config = config or IntelligenceConfig.from_env()
        self.config.resolve()

    @property
    def data_dir(self) -> str:
        return self.config.data_dir

    @property
    def history_path(self) -> str:
        return self.config.history_path

    @property
    def project_root(self) -> str:
        return self.config.project_root

    def ensure_dirs(self) -> None:
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)


def get_settings() -> IntelligenceSettings:
    """Process-wide singleton settings (lazy)."""
    global _settings
    if _settings is None:
        with _lock:
            if _settings is None:
                _settings = IntelligenceSettings()
    return _settings


def reset_settings(config: IntelligenceConfig | None = None) -> IntelligenceSettings:
    """Replace the singleton (used by tests)."""
    global _settings
    with _lock:
        _settings = IntelligenceSettings(config)
    return _settings
