from __future__ import annotations

import time
from typing import Any

from ..data_models import (
    DataBatch,
    DataRecord,
    DataSourceType,
    IngestionResult,
    IngestionSource,
)
from .collector import BaseCollector, CollectorManager
from .connector import BaseConnector, ConnectorManager


class IngestionEngine:
    """Data ingestion — collects records from API, DB, file, event, log, agent and project sources."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.ingestion
        self.connectors = ConnectorManager(engine=engine)
        self.collectors = CollectorManager(engine=engine)
        self._sources: dict[str, IngestionSource] = {}
        self._batches: dict[str, DataBatch] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        await self.connectors.connect_all()

    async def shutdown(self) -> None:
        await self.connectors.disconnect_all()
        self._initialized = False

    def register_source(
        self,
        name: str,
        source_type: DataSourceType = DataSourceType.API,
        config: dict[str, Any] | None = None,
    ) -> IngestionSource:
        source = IngestionSource(
            name=name,
            source_type=source_type,
            config=config or {},
        )
        self._sources[source.source_id] = source
        self.engine.registry.register_source(name, source)
        return source

    def get_source(self, name: str) -> IngestionSource | None:
        for source in self._sources.values():
            if source.name == name:
                return source
        return None

    def list_sources(self) -> list[IngestionSource]:
        return list(self._sources.values())

    def register_connector(self, connector: BaseConnector) -> BaseConnector:
        """Register a connector (API, DB, file) as an ingestible source."""
        self.connectors.register(connector)
        if self.get_source(connector.name) is None:
            self.register_source(
                connector.name,
                source_type=connector.get_source_type(),
                config=connector.config,
            )
        return connector

    def register_collector(self, collector: BaseCollector) -> BaseCollector:
        """Register a collector (event, log, agent, project) as an ingestible source."""
        self.collectors.register(collector)
        if self.get_source(collector.name) is None:
            self.register_source(
                collector.name,
                source_type=collector.get_source_type(),
                config=collector.config,
            )
        return collector

    async def ingest(
        self,
        source: str,
        config: dict[str, Any] | None = None,
    ) -> DataBatch:
        """Collect a batch of records from a named source.

        Resolution order: registered connector → registered collector →
        legacy registry connector → synthesized records from config.
        """
        started = time.perf_counter()
        records: list[DataRecord] = []

        connector = self.connectors.get(source)
        if connector is not None:
            await connector.connect()
            try:
                rows = await connector.read(config or {})
            finally:
                await connector.disconnect()
            records = [
                DataRecord(source=source, data=dict(row), metadata={"connector": source})
                for row in rows
            ]
        else:
            collector = self.collectors.get(source)
            if collector is not None:
                batch = await collector.collect(config or {})
                records = batch.records
            else:
                legacy = self.engine.registry.get_connector(source)
                if legacy is not None and hasattr(legacy, "read"):
                    rows = await legacy.read(config or {})
                    records = [
                        DataRecord(source=source, data=dict(row), metadata={"connector": source})
                        for row in rows
                    ]
                else:
                    # Synthesize a batch from the config (e.g. count + template)
                    count = int((config or {}).get("count", 0))
                    for i in range(count):
                        records.append(DataRecord(
                            source=source,
                            data={(config or {}).get("field", "value"): i},
                        ))

        batch = DataBatch(
            source=source,
            records=records,
            size_bytes=sum(len(str(r.data)) for r in records),
            metadata={"config": config or {}},
        )
        self._batches[batch.batch_id] = batch
        self.engine.runtime.increment("batches_ingested")
        self.engine.metrics.increment("ingestion.batches")
        self.engine.metrics.observe("ingestion.records_per_batch", len(records))

        result = IngestionResult(
            source=source,
            records_count=len(records),
            duration_ms=(time.perf_counter() - started) * 1000,
        )
        await self._notify(batch, result)
        return batch

    async def _notify(self, batch: DataBatch, result: IngestionResult) -> None:
        await self.engine.event_bus.emit("data.ingested", {
            "batch_id": batch.batch_id,
            "source": batch.source,
            "records": len(batch.records),
            "status": result.status,
        })

    def get_batch(self, batch_id: str) -> DataBatch | None:
        return self._batches.get(batch_id)

    def recent_batches(self, source: str, limit: int = 10) -> list[DataBatch]:
        """Return the most recent batches ingested from a given source."""
        matches = [b for b in self._batches.values() if b.source == source]
        return matches[-limit:]

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "sources": len(self._sources),
            "batches": len(self._batches),
            "connectors": self.connectors.status(),
            "collectors": self.collectors.status(),
        }


__all__ = ["IngestionEngine"]
