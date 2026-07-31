"""Data Platform Factory — Factory for creating data platform components."""
from typing import Dict, Any, List, Optional
from .data_models import DataSource, DataRecord, DataPipeline, DataSchema, DataCatalogEntry, DataPartition, DataLineage
from .data_models import DataSourceType, DataFormat, PipelineStatus, StorageTier, DataQualityLevel


class DataPlatformFactory:
    @staticmethod
    def create_source(name: str, source_type: str = "database", connection: str = "", fmt: str = "json") -> DataSource:
        st = DataSourceType(source_type) if source_type in [e.value for e in DataSourceType] else DataSourceType.DATABASE
        df = DataFormat(fmt) if fmt in [e.value for e in DataFormat] else DataFormat.JSON
        return DataSource(name=name, source_type=st, connection_string=connection, format=df)

    @staticmethod
    def create_record(source_id: str, dataset: str, payload: Dict[str, Any], tags: List[str] = None) -> DataRecord:
        return DataRecord(source_id=source_id, dataset=dataset, payload=payload, tags=tags or [])

    @staticmethod
    def create_pipeline(name: str, source_id: str, steps: List[Dict[str, Any]] = None) -> DataPipeline:
        return DataPipeline(name=name, source_id=source_id, steps=steps or [])

    @staticmethod
    def create_schema(name: str, dataset: str, fields: List[Dict[str, Any]], version: str = "1.0") -> DataSchema:
        return DataSchema(name=name, dataset=dataset, fields=fields, version=version)

    @staticmethod
    def create_catalog_entry(dataset: str, description: str, owner: str, tags: List[str] = None) -> DataCatalogEntry:
        return DataCatalogEntry(dataset=dataset, description=description, owner=owner, tags=tags or [])

    @staticmethod
    def create_partition(dataset: str, key: str, tier: str = "hot") -> DataPartition:
        st = StorageTier(tier) if tier in [e.value for e in StorageTier] else StorageTier.HOT
        return DataPartition(dataset=dataset, key=key, tier=st)

    @staticmethod
    def create_lineage(dataset: str, source_datasets: List[str], transformation: str) -> DataLineage:
        return DataLineage(dataset=dataset, source_datasets=source_datasets, transformation=transformation)

    @staticmethod
    def templates() -> Dict[str, Dict[str, Any]]:
        return {
            "sales_data": {
                "fields": [
                    {"name": "order_id", "type": "string", "nullable": False},
                    {"name": "customer_id", "type": "string", "nullable": False},
                    {"name": "amount", "type": "float", "nullable": False},
                    {"name": "timestamp", "type": "datetime", "nullable": False},
                ],
                "source_type": "database",
                "format": "json",
            },
            "sensor_data": {
                "fields": [
                    {"name": "sensor_id", "type": "string", "nullable": False},
                    {"name": "value", "type": "float", "nullable": False},
                    {"name": "unit", "type": "string", "nullable": True},
                    {"name": "timestamp", "type": "datetime", "nullable": False},
                ],
                "source_type": "sensor",
                "format": "json",
            },
            "user_events": {
                "fields": [
                    {"name": "event_id", "type": "string", "nullable": False},
                    {"name": "user_id", "type": "string", "nullable": False},
                    {"name": "event_type", "type": "string", "nullable": False},
                    {"name": "properties", "type": "dict", "nullable": True},
                    {"name": "timestamp", "type": "datetime", "nullable": False},
                ],
                "source_type": "stream",
                "format": "json",
            },
        }
