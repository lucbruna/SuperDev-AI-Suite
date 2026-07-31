"""Manager for the Data Intelligence Engine.

Coordinates ingestion, processing and analytics against registered
datasources. Subsystem engines are attached lazily by the engine facade.
"""

from __future__ import annotations

from typing import Any

from data_intelligence.data_events import DataIntelligenceEventType
from data_intelligence.data_logger import get_logger
from data_intelligence.data_models import DataSource


class DataIntelligenceManager:
    """High-level operations over the engine's registries."""

    def __init__(self, registry: Any, events: Any, metrics: Any,
                 config: Any, context: Any,
                 engine: Any = None) -> None:
        self._log = get_logger()
        self.registry = registry
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.engine: Any = engine

    def register_source(self, source_id: str, name: str,
                        source_type: Any, **config: Any) -> DataSource:
        source = DataSource(source_id=source_id, name=name,
                            source_type=source_type, config=config)
        self.registry.register_source(source_id, source)
        return source

    def list_sources(self) -> list[str]:
        return self.registry.list_sources()

    def get_source(self, source_id: str) -> DataSource | None:
        return self.registry.get_source(source_id)

    def remove_source(self, source_id: str) -> bool:
        return self.registry.remove_source(source_id)

    def ingest(self, source_id: str,
               records: list[dict[str, Any]]) -> dict[str, Any]:
        """Ingests raw records from a source into the engine.

        Delegates to the ingestion engine when attached (set via
        ``with_ingestion``); otherwise records are counted only.
        """
        source = self.registry.get_source(source_id)
        if source is None:
            raise ValueError(f"unknown source: {source_id}")
        self.events.publish(DataIntelligenceEventType.INGESTION_STARTED,
                            {"source_id": source_id})
        ingestion = getattr(self, "ingestion_engine", None)
        if ingestion is not None:
            result = ingestion.ingest(source, records)
        else:
            result = {"ingested": len(records)}
        self.metrics.increment("ingestions.completed")
        self.events.publish(DataIntelligenceEventType.INGESTION_COMPLETED,
                            {"source_id": source_id, "count": len(records)})
        return result

    def analyze(self, metric: str,
                records: list[dict[str, Any]]) -> dict[str, Any]:
        """Runs an analytics computation (delegates to analytics engine)."""
        analytics = getattr(self, "analytics_engine", None)
        if analytics is None:
            raise RuntimeError("analytics engine not attached")
        return analytics.compute(metric, records)

    def stats(self) -> dict[str, Any]:
        return self.registry.stats()
