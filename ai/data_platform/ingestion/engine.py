"""Ingestion engine."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from .models import Connector, IngestionBatch, DataSource, IngestionLog, ConnectorType, IngestionStatus


class IngestionEngine:
    def __init__(self):
        self._connectors: Dict[str, Connector] = {}
        self._batches: Dict[str, IngestionBatch] = {}
        self._sources: Dict[str, DataSource] = {}
        self._logs: List[IngestionLog] = []

    def register_connector(self, connector: Connector) -> Connector:
        self._connectors[connector.connector_id] = connector
        return connector

    def get_connector(self, connector_id: str) -> Optional[Connector]:
        return self._connectors.get(connector_id)

    def register_source(self, source: DataSource) -> DataSource:
        self._sources[source.source_id] = source
        return source

    def get_source(self, source_id: str) -> Optional[DataSource]:
        return self._sources.get(source_id)

    def create_batch(self, connector_id: str, records: List[Dict[str, Any]]) -> IngestionBatch:
        batch = IngestionBatch(
            batch_id=str(uuid.uuid4())[:8],
            connector_id=connector_id,
            records=records,
            record_count=len(records),
            status=IngestionStatus.INGESTING,
            started_at=datetime.now(),
        )
        self._batches[batch.batch_id] = batch
        return batch

    def complete_batch(self, batch_id: str) -> bool:
        batch = self._batches.get(batch_id)
        if not batch:
            return False
        batch.status = IngestionStatus.COMPLETED
        batch.completed_at = datetime.now()
        connector = self._connectors.get(batch.connector_id)
        if connector:
            connector.records_ingested += batch.record_count
            connector.last_run = datetime.now()
        return True

    def fail_batch(self, batch_id: str, error_count: int = 1) -> bool:
        batch = self._batches.get(batch_id)
        if not batch:
            return False
        batch.status = IngestionStatus.FAILED
        batch.error_count = error_count
        return True

    def get_batch(self, batch_id: str) -> Optional[IngestionBatch]:
        return self._batches.get(batch_id)

    def get_connector_batches(self, connector_id: str) -> List[IngestionBatch]:
        return [b for b in self._batches.values() if b.connector_id == connector_id]

    def add_log(self, log: IngestionLog) -> IngestionLog:
        self._logs.append(log)
        return log

    def get_logs(self, connector_id: Optional[str] = None) -> List[IngestionLog]:
        if connector_id:
            return [l for l in self._logs if l.connector_id == connector_id]
        return list(self._logs)

    def get_stats(self) -> dict:
        connectors = list(self._connectors.values())
        return {
            "connectors": len(connectors),
            "sources": len(self._sources),
            "batches": len(self._batches),
            "total_records_ingested": sum(c.records_ingested for c in connectors),
        }
