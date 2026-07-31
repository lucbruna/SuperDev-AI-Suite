from __future__ import annotations

import statistics
from typing import Any

from ..data_models import DataBatch, DataRecord, DataState, DataQualityStatus


class ProcessingEngine:
    """Data processing — transform, clean, normalize, validate, enrich, aggregate, dedupe, anonymize."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.processing
        self._transformers: dict[str, Any] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    def register_transformer(self, name: str, transformer: Any) -> None:
        self._transformers[name] = transformer
        self.engine.registry.register_transformer(name, transformer)

    # -- record-level operations ---------------------------------------------

    def clean(self, record: DataRecord) -> DataRecord:
        record.data = {
            k: v for k, v in record.data.items()
            if v is not None and not (isinstance(v, str) and not v.strip())
        }
        record.state = DataState.CLEANED
        return record

    def normalize(self, record: DataRecord, fields: list[str] | None = None) -> DataRecord:
        keys = fields or list(record.data)
        for key in keys:
            value = record.data.get(key)
            if isinstance(value, str):
                record.data[key] = value.strip().lower()
        return record

    def validate(self, record: DataRecord, rules: dict[str, Any] | None = None) -> bool:
        for key, rule in (rules or {}).items():
            value = record.data.get(key)
            if rule == "required" and value is None:
                return False
            if rule == "numeric" and not isinstance(value, (int, float)):
                return False
        record.quality = DataQualityStatus.GOOD
        return True

    def enrich(self, record: DataRecord, extra: dict[str, Any] | None = None) -> DataRecord:
        record.data.update(extra or {})
        record.metadata["enriched"] = True
        return record

    def anonymize(self, record: DataRecord) -> DataRecord:
        return self.engine.security.mask_pii(record)

    def deduplicate(self, records: list[DataRecord], key: str = "id") -> list[DataRecord]:
        seen: set[Any] = set()
        unique: list[DataRecord] = []
        for record in records:
            marker = record.data.get(key, record.id)
            if marker not in seen:
                seen.add(marker)
                unique.append(record)
        return unique

    # -- batch-level operations ----------------------------------------------

    async def process_batch(self, batch: DataBatch) -> DataBatch:
        processed = DataBatch(
            batch_id=batch.batch_id,
            source=batch.source,
            records=list(batch.records),
            created_at=batch.created_at,
            size_bytes=batch.size_bytes,
            metadata=dict(batch.metadata),
        )

        if self.config.auto_clean:
            processed.records = [self.clean(r) for r in processed.records]
        if self.config.auto_normalize:
            processed.records = [self.normalize(r) for r in processed.records]
        if self.config.anonymize_pii:
            processed.records = [self.anonymize(r) for r in processed.records]
        if self.config.deduplicate:
            processed.records = self.deduplicate(processed.records)

        for record in processed.records:
            record.state = DataState.PROCESSED
            self.engine.metrics.record_record(record)

        await self.engine.event_bus.emit("data.processed", {
            "batch_id": batch.batch_id,
            "records": len(processed.records),
        })
        return processed

    def aggregate(self, records: list[DataRecord], field: str) -> dict[str, float]:
        values = [
            record.data[field]
            for record in records
            if isinstance(record.data.get(field), (int, float))
        ]
        if not values:
            return {"count": 0, "sum": 0.0}
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": statistics.mean(values),
            "min": min(values),
            "max": max(values),
        }

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "transformers": len(self._transformers),
        }


__all__ = ["ProcessingEngine"]
