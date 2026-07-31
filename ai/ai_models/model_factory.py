"""AI Model factory."""

from __future__ import annotations

from .model_config import ModelConfig
from .model_context import ModelContext
from .model_events import ModelEvents
from .model_logger import ModelLogger
from .model_metrics import ModelMetrics
from .model_registry import ModelRegistry
from .model_runtime import ModelRuntime
from .model_security import ModelSecurity


class ModelFactory:
    def __init__(self, config: ModelConfig | None = None) -> None:
        self._config = config or ModelConfig()
        self._logger: ModelLogger | None = None
        self._metrics: ModelMetrics | None = None
        self._events: ModelEvents | None = None
        self._context: ModelContext | None = None
        self._registry: ModelRegistry | None = None
        self._runtime: ModelRuntime | None = None
        self._security: ModelSecurity | None = None

    def create_logger(self) -> ModelLogger:
        if not self._logger:
            self._logger = ModelLogger()
        return self._logger

    def create_metrics(self) -> ModelMetrics:
        if not self._metrics:
            self._metrics = ModelMetrics()
        return self._metrics

    def create_events(self) -> ModelEvents:
        if not self._events:
            self._events = ModelEvents()
        return self._events

    def create_context(self) -> ModelContext:
        if not self._context:
            self._context = ModelContext()
        return self._context

    def create_registry(self) -> ModelRegistry:
        if not self._registry:
            self._registry = ModelRegistry()
        return self._registry

    def create_runtime(self) -> ModelRuntime:
        if not self._runtime:
            self._runtime = ModelRuntime()
        return self._runtime

    def create_security(self) -> ModelSecurity:
        if not self._security:
            self._security = ModelSecurity()
        return self._security

    def get_config(self) -> ModelConfig:
        return self._config
