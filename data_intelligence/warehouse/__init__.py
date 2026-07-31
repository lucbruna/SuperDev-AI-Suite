"""Warehouse subsystem (Volume 22).

Stores structured, query-ready data in star schemas (dimensions + facts)
backed by in-memory tables and a staging area.
"""

from __future__ import annotations

from data_intelligence.warehouse.base import WarehouseError, WarehouseTable
from data_intelligence.warehouse.dimension import DimensionTable
from data_intelligence.warehouse.engine import WarehouseEngine
from data_intelligence.warehouse.fact import FactTable
from data_intelligence.warehouse.loader import StagingArea
from data_intelligence.warehouse.schema import StarSchema

__all__ = [
    "WarehouseEngine", "WarehouseTable", "DimensionTable", "FactTable",
    "StarSchema", "StagingArea", "WarehouseError",
]
