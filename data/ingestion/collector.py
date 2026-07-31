from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..data_models import DataBatch, DataRecord, DataSourceType


class BaseCollector(ABC):
    """Abstract data collector.

    Collectors gather records from a specific domain (API, database, file,
    events, logs, agents, projects) and package them into :class:`DataBatch`.
    """

    def __init__(
        self,
        name: str,
        engine: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.engine = engine
        self.config = config or {}
        self._collected_count = 0

    @abstractmethod
    async def collect(self, config: dict[str, Any] | None = None) -> DataBatch:
        """Collect a batch of data records."""

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.API

    def _build_batch(
        self,
        rows: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> DataBatch:
        records = [
            DataRecord(
                source=self.name,
                data=dict(row),
                metadata={"collector": self.name},
            )
            for row in rows
        ]
        self._collected_count += len(records)
        return DataBatch(
            source=self.name,
            records=records,
            size_bytes=sum(len(str(r)) for r in rows),
            metadata=metadata or {},
        )

    def get_status(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": type(self).__name__,
            "source_type": self.get_source_type().value,
            "collected": self._collected_count,
        }


class CollectorManager:
    """Registry and lifecycle manager for collectors."""

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._collectors: dict[str, BaseCollector] = {}

    def register(self, collector: BaseCollector) -> BaseCollector:
        self._collectors[collector.name] = collector
        return collector

    def unregister(self, name: str) -> bool:
        return self._collectors.pop(name, None) is not None

    def get(self, name: str) -> BaseCollector | None:
        return self._collectors.get(name)

    def list(self) -> list[BaseCollector]:
        return list(self._collectors.values())

    def names(self) -> list[str]:
        return list(self._collectors.keys())

    async def collect(self, name: str, config: dict[str, Any] | None = None) -> DataBatch:
        collector = self._collectors.get(name)
        if collector is None:
            raise ValueError(f"Collector not registered: {name}")
        batch = await collector.collect(config or {})
        if self.engine is not None:
            self.engine.metrics.increment("ingestion.collector_runs", labels={"collector": name})
        return batch

    def status(self) -> dict[str, Any]:
        return {
            "collectors": {
                name: collector.get_status()
                for name, collector in self._collectors.items()
            },
            "count": len(self._collectors),
        }


__all__ = ["BaseCollector", "CollectorManager"]
