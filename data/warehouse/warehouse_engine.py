from __future__ import annotations

from typing import Any

from ..data_models import DataRecord, Dimension, FactTable, StarSchema


class WarehouseEngine:
    """Corporate Data Warehouse — star/snowflake schemas, partitioning, optimization."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.warehouse
        self._schemas: dict[str, StarSchema] = {}
        self._tables: dict[str, list[dict[str, Any]]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    def create_star_schema(
        self,
        name: str,
        fact: FactTable | None = None,
        dimensions: list[Dimension] | None = None,
    ) -> StarSchema:
        schema = StarSchema(
            name=name,
            fact=fact or FactTable(name=f"fact_{name}"),
            dimensions=dimensions or [],
        )
        self._schemas[name] = schema
        self.engine.registry.register_schema(schema)
        self._tables.setdefault(schema.fact.name, [])
        for dim in schema.dimensions:
            self._tables.setdefault(dim.name, [])
        return schema

    def get_schema(self, name: str) -> StarSchema | None:
        return self._schemas.get(name)

    def list_schemas(self) -> list[StarSchema]:
        return list(self._schemas.values())

    async def insert(self, table: str, records: list[DataRecord]) -> int:
        rows = self._tables.setdefault(table, [])
        for record in records:
            rows.append(dict(record.data, _id=record.id, _ts=record.timestamp))
        self.engine.metrics.increment("warehouse.inserts", len(records))
        return len(records)

    def query(self, table: str, limit: int = 100) -> list[dict[str, Any]]:
        return self._tables.get(table, [])[-limit:]

    def table_stats(self, table: str) -> dict[str, Any]:
        rows = self._tables.get(table, [])
        return {
            "table": table,
            "rows": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
        }

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "schemas": len(self._schemas),
            "tables": len(self._tables),
        }


__all__ = ["WarehouseEngine"]
