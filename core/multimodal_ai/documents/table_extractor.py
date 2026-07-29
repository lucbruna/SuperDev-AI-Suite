from __future__ import annotations

import uuid
from typing import Any, Optional

SAMPLE_TABLES: list[dict[str, Any]] = [
    {
        "id": "t1",
        "name": "Sales Report Q1",
        "headers": ["Product", "Units Sold", "Revenue", "Region"],
        "rows": [
            ["Widget A", "1200", "$24,000", "North"],
            ["Widget B", "850", "$17,000", "South"],
            ["Widget C", "2100", "$42,000", "East"],
            ["Widget D", "950", "$19,000", "West"],
        ],
    },
    {
        "id": "t2",
        "name": "Employee List",
        "headers": ["Name", "Department", "Salary", "Start Date"],
        "rows": [
            ["Alice Smith", "Engineering", "$95,000", "2023-01-15"],
            ["Bob Jones", "Marketing", "$78,000", "2023-03-01"],
            ["Carol Lee", "Finance", "$88,000", "2022-11-20"],
        ],
    },
    {
        "id": "t3",
        "name": "Inventory Count",
        "headers": ["SKU", "Item", "Quantity", "Location"],
        "rows": [
            ["SKU-001", "Laptop", "45", "Warehouse A"],
            ["SKU-002", "Monitor", "120", "Warehouse B"],
            ["SKU-003", "Keyboard", "300", "Warehouse A"],
            ["SKU-004", "Mouse", "500", "Warehouse C"],
        ],
    },
]


class TableExtractor:
    def __init__(self) -> None:
        self._extracted_tables: dict[str, list[dict[str, Any]]] = {}

    async def extract_tables(self, document: dict[str, Any]) -> list[dict[str, Any]]:
        doc_id = document.get("id", document.get("document_id", uuid.uuid4().hex))
        tables = [dict(t) for t in SAMPLE_TABLES]
        self._extracted_tables[doc_id] = tables
        return tables

    async def parse_table(self, table: dict[str, Any]) -> list[dict[str, str]]:
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        return [dict(zip(headers, row)) for row in rows]

    async def extract_cells(self, table: dict[str, Any], row_index: int, col_index: int) -> Optional[str]:
        rows = table.get("rows", [])
        if 0 <= row_index < len(rows):
            cols = rows[row_index]
            if 0 <= col_index < len(cols):
                return cols[col_index]
        return None

    async def detect_table_structure(self, table: dict[str, Any]) -> dict[str, Any]:
        rows = table.get("rows", [])
        headers = table.get("headers", [])
        return {
            "row_count": len(rows),
            "column_count": len(headers),
            "has_header": len(headers) > 0,
            "is_rectangular": all(len(r) == len(headers) for r in rows),
            "headers": headers,
        }

    async def export_to_dict(self, table: dict[str, Any]) -> list[dict[str, str]]:
        return await self.parse_table(table)
