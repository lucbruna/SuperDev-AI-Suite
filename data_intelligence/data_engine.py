"""Data Intelligence & Analytics Engine (Volume 22).

Facade that wires the core services and exposes subsystem engines lazily
(``engine.ingestion``, ``engine.analytics``, ...) once they are attached by
``attach_subsystem``.
"""

from __future__ import annotations

from typing import Any

from data_intelligence.data_config import DataIntelligenceConfig
from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_events import (DataIntelligenceEventType,
                                           DataIntelligenceEvents)
from data_intelligence.data_logger import get_logger
from data_intelligence.data_manager import DataIntelligenceManager
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_registry import DataIntelligenceRegistry
from data_intelligence.data_runtime import DataIntelligenceRuntime
from data_intelligence.data_security import DataIntelligenceSecurity


class DataIntelligenceEngine:
    """Aggregate facade over the Data Intelligence subsystems."""

    def __init__(self, config: DataIntelligenceConfig | None = None,
                 events: DataIntelligenceEvents | None = None,
                 metrics: DataIntelligenceMetrics | None = None,
                 registry: DataIntelligenceRegistry | None = None,
                 security: DataIntelligenceSecurity | None = None,
                 context: DataIntelligenceContext | None = None,
                 runtime: DataIntelligenceRuntime | None = None) -> None:
        self._log = get_logger()
        self.config = config or DataIntelligenceConfig()
        self.events = events or DataIntelligenceEvents()
        self.metrics = metrics or DataIntelligenceMetrics()
        self.registry = registry or DataIntelligenceRegistry()
        self.security = security or DataIntelligenceSecurity()
        self.context = context or DataIntelligenceContext()
        self.runtime = runtime or DataIntelligenceRuntime()
        self.manager = DataIntelligenceManager(
            registry=self.registry, events=self.events, metrics=self.metrics,
            config=self.config, context=self.context, engine=self)
        self._subsystems: dict[str, Any] = {}

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> bool:
        return self.runtime.start()

    def stop(self) -> bool:
        return self.runtime.stop()

    # -- subsystem attachment ----------------------------------------------
    def attach_subsystem(self, name: str, engine: Any) -> None:
        """Attaches a subsystem engine (lazy attribute access)."""
        self._subsystems[name] = engine
        setattr(self, name, engine)
        # Let the manager reach subsystem engines too.
        setattr(self.manager, f"{name}_engine", engine)

    def __getattr__(self, name: str) -> Any:
        if name in self._subsystems:
            return self._subsystems[name]
        raise AttributeError(f"no subsystem or attribute '{name}'")

    # -- datasources -------------------------------------------------------
    def register_source(self, source_id: str, name: str,
                        source_type: Any, **config: Any) -> Any:
        return self.manager.register_source(source_id, name, source_type,
                                            **config)

    def list_sources(self) -> list[str]:
        return self.manager.list_sources()

    def ingest(self, source_id: str,
               records: list[dict[str, Any]]) -> dict[str, Any]:
        return self.manager.ingest(source_id, records)

    # -- analytics ---------------------------------------------------------
    def analyze(self, metric: str,
                records: list[dict[str, Any]]) -> dict[str, Any]:
        return self.manager.analyze(metric, records)

    def stats(self) -> dict[str, Any]:
        return {
            "registry": self.registry.stats(),
            "subsystems": list(self._subsystems),
            "metrics": self.metrics.snapshot(),
            "runtime": self.runtime.state(),
        }

    def run(self) -> bool:
        """Convenience alias for start()."""
        return self.start()
