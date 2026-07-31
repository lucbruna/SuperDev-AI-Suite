"""Ingestion collector engine.

Coordinates all registered datasources: fetches raw records through the
configured connectors and normalizes them into ``DataRecord`` objects.
"""

from __future__ import annotations

from typing import Any, Iterable

from data_intelligence.data_events import (DataIntelligenceEventType,
                                           DataIntelligenceEvents)
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import DataRecord, DataSource
from data_intelligence.ingestion.base import BaseSource
from data_intelligence.ingestion.erp_crm_source import CrmSource, ErpSource
from data_intelligence.ingestion.api_source import ApiSource
from data_intelligence.ingestion.file_source import FileSource
from data_intelligence.ingestion.nosql_source import MongoSource
from data_intelligence.ingestion.sql_source import SqlSource
from data_intelligence.ingestion.stream_source import StreamSource


class IngestionCollector:
    """Ingestion engine that the facade attaches as ``ingestion``."""

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.sources: dict[str, BaseSource] = {}
        self._last_batches: dict[str, list[DataRecord]] = {}

    # -- registration ------------------------------------------------------
    def add_source(self, source: BaseSource) -> None:
        """Registers a configured source connector."""
        self.sources[source.source_id] = source
        self._log.info("registered ingestion source %s (%s)",
                       source.source_id, type(source).__name__)

    # -- fetching ----------------------------------------------------------
    def fetch(self, source_id: str,
              tags: Iterable[str] | None = None) -> list[DataRecord]:
        """Fetches raw records from a registered source as DataRecords."""
        source = self.sources.get(source_id)
        if source is None:
            raise ValueError(f"no connector for source: {source_id}")
        rows = list(source.fetch(source))
        records = source.records(rows, tags=tags)
        self._last_batches[source_id] = records
        self.metrics.increment("ingestion.records")
        return records

    # -- normalization -----------------------------------------------------
    def normalize(self, records: list[DataRecord]) -> list[DataRecord]:
        """Returns records unchanged (processing happens in pipelines)."""
        return records

    # -- public API used by the manager ------------------------------------
    def ingest(self, source: DataSource,
               records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Ingests records for a registered datasource.

        When ``records`` is None the collector fetches from the configured
        connector; otherwise the given raw records are wrapped into
        ``DataRecord`` objects.
        """
        source_id = source.source_id
        self.events.publish(DataIntelligenceEventType.INGESTION_STARTED,
                            {"source_id": source_id})
        try:
            if records is not None:
                wrapped = self._wrap(source, records)
            else:
                wrapped = self.fetch(source_id, tags=[source.name])
            self._last_batches[source_id] = wrapped
            result = {"ingested": len(wrapped), "source_id": source_id,
                      "records": wrapped}
            self.metrics.gauge(f"ingestion.batch.{source_id}", len(wrapped))
            self.events.publish(DataIntelligenceEventType.INGESTION_COMPLETED,
                                {"source_id": source_id,
                                 "count": len(wrapped)})
            return result
        except Exception as exc:  # noqa: BLE001
            self.events.publish(DataIntelligenceEventType.INGESTION_FAILED,
                                {"source_id": source_id,
                                 "error": str(exc)})
            raise

    def _wrap(self, source: DataSource,
              records: list[dict[str, Any]]) -> list[DataRecord]:
        return [DataRecord(record_id=f"rec-{i}", source_id=source_id,
                           data=dict(record), tags=[source.name])
                for i, record in enumerate(records)
                for source_id in [source.source_id]]

    def latest_batch(self, source_id: str) -> list[DataRecord]:
        return list(self._last_batches.get(source_id, []))

    def stats(self) -> dict[str, Any]:
        return {"sources": list(self.sources),
                "last_batches": {k: len(v)
                                 for k, v in self._last_batches.items()}}


__all__ = [
    "IngestionCollector", "BaseSource", "SqlSource", "MongoSource",
    "ApiSource", "FileSource", "StreamSource", "ErpSource", "CrmSource",
]
