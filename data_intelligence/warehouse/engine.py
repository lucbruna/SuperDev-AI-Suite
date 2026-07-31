"""Warehouse engine (attached by the facade as ``warehouse``).

Implements ``DataSink.write`` so pipelines can land results here.
"""

from __future__ import annotations

from typing import Any, Iterable

from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.warehouse.base import WarehouseTable
from data_intelligence.warehouse.dimension import DimensionTable
from data_intelligence.warehouse.fact import FactTable
from data_intelligence.warehouse.loader import StagingArea
from data_intelligence.warehouse.schema import StarSchema


class WarehouseEngine:
    """Coordinates warehouse tables, schemas and the staging area."""

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.tables: dict[str, WarehouseTable] = {}
        self.schemas: dict[str, StarSchema] = {}
        self.staging = StagingArea()

    # -- tables ------------------------------------------------------------
    def create_table(self, name: str, columns: dict[str, str],
                     primary_key: str = "id",
                     kind: str = "regular") -> WarehouseTable:
        if kind == "dimension":
            table: WarehouseTable = DimensionTable(name, columns,
                                                   primary_key)
        elif kind == "fact":
            measures = [c for c, t in columns.items() if t == "number"]
            table = FactTable(name, columns, primary_key,
                              measures=measures,
                              dimensions=[c for c in columns
                                          if c.endswith("_id")])
        else:
            table = WarehouseTable(name, columns, primary_key)
        self.tables[name] = table
        return table

    def create_schema(self, name: str) -> StarSchema:
        schema = StarSchema(name)
        self.schemas[name] = schema
        return schema

    # -- DataSink protocol ---------------------------------------------------
    def write(self, records: Iterable[dict[str, Any]],
              destination: Any) -> dict[str, Any]:
        """Writes records into a table (destination = table name)."""
        table = self.tables.get(str(destination))
        if table is None:
            raise ValueError(f"unknown warehouse table: {destination}")
        count = table.insert_many(records)
        self.metrics.increment("warehouse.writes")
        return {"table": table.name, "written": count}

    def query(self, table: str) -> list[dict[str, Any]]:
        table_obj = self.tables.get(table)
        if table_obj is None:
            raise ValueError(f"unknown warehouse table: {table}")
        return table_obj.all()

    def count(self, table: str) -> int:
        table_obj = self.tables.get(table)
        return table_obj.count() if table_obj else 0

    def stats(self) -> dict[str, Any]:
        return {
            "tables": {name: table.count()
                       for name, table in self.tables.items()},
            "schemas": list(self.schemas),
            "staging": self.staging.pending(),
        }
