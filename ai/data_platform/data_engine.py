"""Data Platform Engine — Core data platform engine."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from .data_models import (
    DataSource, DataRecord, DataPipeline, DataSchema, DataCatalogEntry,
    DataPartition, DataLineage, DataSourceType, PipelineStatus, DataQualityLevel, StorageTier,
)
from .data_config import DataPlatformConfig


class DataPlatformEngine:
    def __init__(self, config: Optional[DataPlatformConfig] = None):
        self._config = config or DataPlatformConfig()
        self._sources: Dict[str, DataSource] = {}
        self._records: Dict[str, DataRecord] = {}
        self._pipelines: Dict[str, DataPipeline] = {}
        self._schemas: Dict[str, DataSchema] = {}
        self._catalog: Dict[str, DataCatalogEntry] = {}
        self._partitions: Dict[str, DataPartition] = {}
        self._lineage: List[DataLineage] = []

    def register_source(self, source: DataSource) -> DataSource:
        self._sources[source.source_id] = source
        return source

    def get_source(self, source_id: str) -> Optional[DataSource]:
        return self._sources.get(source_id)

    def list_sources(self) -> List[DataSource]:
        return list(self._sources.values())

    def ingest_record(self, record: DataRecord) -> DataRecord:
        self._records[record.record_id] = record
        return record

    def get_record(self, record_id: str) -> Optional[DataRecord]:
        return self._records.get(record_id)

    def query_records(self, dataset: str, filters: Optional[Dict[str, Any]] = None) -> List[DataRecord]:
        records = [r for r in self._records.values() if r.dataset == dataset]
        if filters:
            for key, value in filters.items():
                records = [r for r in records if r.payload.get(key) == value]
        return records

    def create_pipeline(self, pipeline: DataPipeline) -> DataPipeline:
        self._pipelines[pipeline.pipeline_id] = pipeline
        return pipeline

    def get_pipeline(self, pipeline_id: str) -> Optional[DataPipeline]:
        return self._pipelines.get(pipeline_id)

    def start_pipeline(self, pipeline_id: str) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = datetime.now()
        return True

    def complete_pipeline(self, pipeline_id: str, records_processed: int = 0) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        pipeline.status = PipelineStatus.COMPLETED
        pipeline.records_processed = records_processed
        pipeline.completed_at = datetime.now()
        return True

    def fail_pipeline(self, pipeline_id: str, error_count: int = 1) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        pipeline.status = PipelineStatus.FAILED
        pipeline.error_count = error_count
        return True

    def register_schema(self, schema: DataSchema) -> DataSchema:
        self._schemas[schema.schema_id] = schema
        return schema

    def get_schema(self, schema_id: str) -> Optional[DataSchema]:
        return self._schemas.get(schema_id)

    def add_catalog_entry(self, entry: DataCatalogEntry) -> DataCatalogEntry:
        self._catalog[entry.entry_id] = entry
        return entry

    def get_catalog_entry(self, entry_id: str) -> Optional[DataCatalogEntry]:
        return self._catalog.get(entry_id)

    def search_catalog(self, query: str) -> List[DataCatalogEntry]:
        q = query.lower()
        return [e for e in self._catalog.values()
                if q in e.dataset.lower() or q in e.description.lower()
                or any(q in t.lower() for t in e.tags)]

    def add_partition(self, partition: DataPartition) -> DataPartition:
        self._partitions[partition.partition_id] = partition
        return partition

    def get_partition(self, partition_id: str) -> Optional[DataPartition]:
        return self._partitions.get(partition_id)

    def add_lineage(self, lineage: DataLineage) -> DataLineage:
        self._lineage.append(lineage)
        return lineage

    def get_lineage(self, dataset: str) -> List[DataLineage]:
        return [l for l in self._lineage if l.dataset == dataset]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "sources": len(self._sources),
            "records": len(self._records),
            "pipelines": len(self._pipelines),
            "schemas": len(self._schemas),
            "catalog_entries": len(self._catalog),
            "partitions": len(self._partitions),
            "lineage_entries": len(self._lineage),
            "active_pipelines": len([p for p in self._pipelines.values() if p.status == PipelineStatus.RUNNING]),
        }
