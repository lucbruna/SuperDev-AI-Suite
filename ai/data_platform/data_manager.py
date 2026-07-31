"""Data Platform Manager — High-level manager for data platform operations."""

from typing import Any

from .data_config import DataPlatformConfig
from .data_engine import DataPlatformEngine
from .data_models import DataCatalogEntry, DataPipeline, DataRecord, DataSchema, DataSource


class DataPlatformManager:
    def __init__(self, config: DataPlatformConfig | None = None):
        self._engine = DataPlatformEngine(config)

    def register_source(self, name: str, source_type: str, connection: str = "") -> DataSource:
        from .data_models import DataSourceType

        st = (
            DataSourceType(source_type) if source_type in [e.value for e in DataSourceType] else DataSourceType.DATABASE
        )
        source = DataSource(name=name, source_type=st, connection_string=connection)
        return self._engine.register_source(source)

    def ingest_data(self, source_id: str, dataset: str, records: list[dict[str, Any]]) -> int:
        count = 0
        for payload in records:
            record = DataRecord(source_id=source_id, dataset=dataset, payload=payload)
            self._engine.ingest_record(record)
            count += 1
        return count

    def query(self, dataset: str, **filters) -> list[DataRecord]:
        return self._engine.query_records(dataset, filters if filters else None)

    def create_pipeline(self, name: str, source_id: str, steps: list[dict[str, Any]] = None) -> DataPipeline:
        pipeline = DataPipeline(name=name, source_id=source_id, steps=steps or [])
        return self._engine.create_pipeline(pipeline)

    def run_pipeline(self, pipeline_id: str, records: list[DataRecord]) -> bool:
        if not self._engine.start_pipeline(pipeline_id):
            return False
        for r in records:
            self._engine.ingest_record(r)
        return self._engine.complete_pipeline(pipeline_id, len(records))

    def register_schema(self, name: str, dataset: str, fields: list[dict[str, Any]]) -> DataSchema:
        schema = DataSchema(name=name, dataset=dataset, fields=fields)
        return self._engine.register_schema(schema)

    def catalog_dataset(self, dataset: str, description: str, owner: str, tags: list[str] = None) -> DataCatalogEntry:
        entry = DataCatalogEntry(dataset=dataset, description=description, owner=owner, tags=tags or [])
        return self._engine.add_catalog_entry(entry)

    def search(self, query: str) -> list[DataCatalogEntry]:
        return self._engine.search_catalog(query)

    def get_stats(self) -> dict[str, Any]:
        return self._engine.get_stats()
