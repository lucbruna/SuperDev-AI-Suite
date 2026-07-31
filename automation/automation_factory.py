"""Factory wiring for the automation engine."""

from __future__ import annotations

from typing import Any

from .automation_config import AutomationConfig
from .automation_context import AutomationContext
from .automation_engine import AutomationEngine
from .automation_events import AutomationEvents
from .automation_logger import get_logger
from .automation_manager import AutomationManager
from .automation_metrics import AutomationMetrics
from .automation_registry import AutomationRegistry
from .automation_runtime import AutomationRuntime
from .automation_security import AutomationSecurity


class AutomationFactory:
    """Builds automation engine components with shared wiring."""

    def __init__(self, config: AutomationConfig | None = None) -> None:
        self.config = config or AutomationConfig()
        self._log = get_logger("factory")

    def build_events(self) -> AutomationEvents:
        return AutomationEvents()

    def build_metrics(self) -> AutomationMetrics:
        return AutomationMetrics()

    def build_security(self) -> AutomationSecurity:
        return AutomationSecurity()

    def build_registry(self) -> AutomationRegistry:
        return AutomationRegistry()

    def build_context(self, workflow_id: str) -> AutomationContext:
        return AutomationContext(workflow_id)

    def build_runtime(self, registry: AutomationRegistry,
                      events: AutomationEvents) -> AutomationRuntime:
        return AutomationRuntime(registry, events)

    def build_manager(self, registry: AutomationRegistry,
                      security: AutomationSecurity,
                      events: AutomationEvents,
                      metrics: AutomationMetrics) -> AutomationManager:
        return AutomationManager(registry, security, events, metrics)

    def build_engine(self, **overrides: Any) -> AutomationEngine:
        """Builds a fully-wired AutomationEngine."""
        config = self.config.merge(**overrides)
        events = self.build_events()
        metrics = self.build_metrics()
        security = self.build_security()
        registry = self.build_registry()
        runtime = self.build_runtime(registry, events)
        manager = self.build_manager(registry, security, events, metrics)
        return AutomationEngine(config, manager, runtime, registry,
                                events, metrics, security)
