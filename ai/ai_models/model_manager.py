"""High-level model manager."""

from __future__ import annotations

from typing import Any

from .model_config import ModelConfig
from .model_factory import ModelFactory
from .model_logger import ModelLogger
from .model_metrics import ModelMetrics


class ModelManager:
    def __init__(self, config: ModelConfig | None = None) -> None:
        self._factory = ModelFactory(config)
        self._logger = self._factory.create_logger()
        self._metrics = self._factory.create_metrics()
        self._events = self._factory.create_events()
        self._registry = self._factory.create_registry()
        self._runtime = self._factory.create_runtime()
        self._security = self._factory.create_security()

    def register_model(self, model_id: str, name: str, provider: str, model_type: str = "llm") -> dict[str, Any]:
        return self._registry.register(model_id, name, provider, model_type)

    def load_model(self, model_id: str) -> dict[str, Any]:
        return self._runtime.load_model(model_id)

    def get_model(self, model_id: str) -> dict[str, Any] | None:
        return self._registry.get(model_id)

    def list_models(self) -> list[dict[str, Any]]:
        return self._registry.list_active()

    def record_cost(self, model_id: str, amount: float) -> None:
        self._metrics.record_cost(model_id, amount)

    def get_cost(self, model_id: str = "") -> float:
        if model_id:
            return self._metrics.get_model_cost(model_id)
        return self._metrics.get_total_cost()

    def start(self) -> None:
        self._runtime.start()
        self._logger.info("Model manager started", "ModelManager")

    def stop(self) -> None:
        self._runtime.stop()
        self._logger.info("Model manager stopped", "ModelManager")

    def get_status(self) -> dict[str, Any]:
        return {
            "running": self._runtime.is_running(),
            "models": self._registry.count(),
            "loaded": self._runtime.count_loaded(),
            "total_cost": self.get_cost(),
        }

    def get_logger(self) -> ModelLogger:
        return self._logger

    def get_metrics(self) -> ModelMetrics:
        return self._metrics

    def get_registry(self) -> ModelRegistry:
        return self._registry

    def get_security(self) -> ModelSecurity:
        return self._security
