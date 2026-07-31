"""Central enterprise engine."""
from __future__ import annotations

from typing import Any

from .enterprise_config import EnterpriseConfig
from .enterprise_manager import EnterpriseManager


class EnterpriseEngine:
    def __init__(self, config: EnterpriseConfig | None = None) -> None:
        self._config = config or EnterpriseConfig()
        self._manager = EnterpriseManager(self._config)
        self._started = False
    def start(self) -> None:
        if not self._started:
            self._manager.start()
            self._started = True
    def stop(self) -> None:
        if self._started:
            self._manager.stop()
            self._started = False
    def is_running(self) -> bool:
        return self._started
    def get_status(self) -> dict[str, Any]:
        return {**self._manager.get_status(), "started": self._started, "config_enabled": self._config.enabled}
    def get_manager(self) -> EnterpriseManager:
        return self._manager
    def get_config(self) -> EnterpriseConfig:
        return self._config
