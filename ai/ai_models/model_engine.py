"""Central AI Model engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from .model_config import ModelConfig
from .model_manager import ModelManager

class ModelEngine:
    def __init__(self, config: Optional[ModelConfig] = None) -> None:
        self._config = config or ModelConfig()
        self._manager = ModelManager(self._config)
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
    def get_status(self) -> Dict[str, Any]:
        return {**self._manager.get_status(), "started": self._started}
    def get_manager(self) -> ModelManager:
        return self._manager
    def get_config(self) -> ModelConfig:
        return self._config
