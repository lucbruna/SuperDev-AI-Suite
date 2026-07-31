"""Star schema builder for the warehouse."""

from __future__ import annotations

from typing import Any

from data_intelligence.warehouse.base import WarehouseError
from data_intelligence.warehouse.dimension import DimensionTable
from data_intelligence.warehouse.fact import FactTable


class StarSchema:
    """Combines dimension and fact tables into one logical schema."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.dimensions: dict[str, DimensionTable] = {}
        self.facts: dict[str, FactTable] = {}

    def add_dimension(self, name: str, columns: dict[str, str],
                      primary_key: str = "id",
                      track_changes: bool = False) -> DimensionTable:
        table = DimensionTable(f"{self.name}_dim_{name}", columns,
                               primary_key, track_changes)
        self.dimensions[name] = table
        return table

    def add_fact(self, name: str, columns: dict[str, str],
                 primary_key: str = "id",
                 measures: list[str] | None = None,
                 dimensions: list[str] | None = None) -> FactTable:
        table = FactTable(f"{self.name}_fact_{name}", columns,
                          primary_key, measures, dimensions)
        self.facts[name] = table
        return table

    def load_fact(self, fact_name: str, records: list[dict[str, Any]],
                  dimension_lookup: dict[str, dict[str, Any]] | None = None,
                  **dimension_foreign_keys: str) -> int:
        """Loads fact records resolving dimension references.

        ``dimension_foreign_keys`` maps dimension name -> record field that
        holds the dimension key. Missing dimension keys raise an error.
        """
        fact = self.facts.get(fact_name)
        if fact is None:
            raise WarehouseError(f"unknown fact table: {fact_name}")
        count = 0
        for record in records:
            resolved = dict(record)
            for dim_name, field in dimension_foreign_keys.items():
                dim = self.dimensions.get(dim_name)
                if dim is None:
                    raise WarehouseError(f"unknown dimension: {dim_name}")
                dim_key = record.get(field)
                if dim_key is None:
                    raise WarehouseError(
                        f"missing dimension key {field!r} for {dim_name}")
                fk = f"{dim_name}_id"
                if fk not in fact.columns:
                    fact.columns[fk] = "number"
                    fact.dimensions.append(fk)
                if dim.get(float(dim_key)) is None and \
                        dim.get(dim_key) is None:
                    raise WarehouseError(
                        f"dimension key {dim_key!r} not found in "
                        f"{dim_name}")
                resolved[fk] = dim_key
            fact.insert(resolved)
            count += 1
        return count

    def stats(self) -> dict[str, Any]:
        return {
            "dimensions": {k: t.count() for k, t in self.dimensions.items()},
            "facts": {k: t.count() for k, t in self.facts.items()},
        }
