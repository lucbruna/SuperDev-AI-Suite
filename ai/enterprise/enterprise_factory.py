"""Enterprise factory."""

from __future__ import annotations

from .enterprise_config import EnterpriseConfig
from .enterprise_context import EnterpriseContext
from .enterprise_events import EnterpriseEvents
from .enterprise_logger import EnterpriseLogger
from .enterprise_metrics import EnterpriseMetrics
from .enterprise_registry import EnterpriseRegistry
from .enterprise_runtime import EnterpriseRuntime
from .enterprise_security import EnterpriseSecurity


class EnterpriseFactory:
    def __init__(self, config: EnterpriseConfig | None = None) -> None:
        self._config = config or EnterpriseConfig()
        self._logger: EnterpriseLogger | None = None
        self._metrics: EnterpriseMetrics | None = None
        self._events: EnterpriseEvents | None = None
        self._context: EnterpriseContext | None = None
        self._registry: EnterpriseRegistry | None = None
        self._runtime: EnterpriseRuntime | None = None
        self._security: EnterpriseSecurity | None = None

    def create_logger(self) -> EnterpriseLogger:
        if not self._logger:
            self._logger = EnterpriseLogger()
        return self._logger

    def create_metrics(self) -> EnterpriseMetrics:
        if not self._metrics:
            self._metrics = EnterpriseMetrics()
        return self._metrics

    def create_events(self) -> EnterpriseEvents:
        if not self._events:
            self._events = EnterpriseEvents()
        return self._events

    def create_context(self) -> EnterpriseContext:
        if not self._context:
            self._context = EnterpriseContext()
        return self._context

    def create_registry(self) -> EnterpriseRegistry:
        if not self._registry:
            self._registry = EnterpriseRegistry()
        return self._registry

    def create_runtime(self) -> EnterpriseRuntime:
        if not self._runtime:
            self._runtime = EnterpriseRuntime()
        return self._runtime

    def create_security(self) -> EnterpriseSecurity:
        if not self._security:
            self._security = EnterpriseSecurity()
        return self._security

    def get_config(self) -> EnterpriseConfig:
        return self._config
