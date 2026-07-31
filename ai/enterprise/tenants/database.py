"""Tenant database."""
from __future__ import annotations
from typing import Any, Dict, List

class TenantDatabase:
    def __init__(self) -> None:
        self._schemas: Dict[str, Dict[str, Any]] = {}
    def create_schema(self, org_id: str, schema_name: str) -> Dict[str, Any]:
        schema = {"org_id": org_id, "schema": schema_name, "tables": [], "status": "active"}
        self._schemas[f"{org_id}:{schema_name}"] = schema
        return schema
    def add_table(self, org_id: str, schema_name: str, table_name: str) -> bool:
        key = f"{org_id}:{schema_name}"
        schema = self._schemas.get(key)
        if schema and table_name not in schema["tables"]:
            schema["tables"].append(table_name)
            return True
        return False
    def get_schema(self, org_id: str, schema_name: str) -> Dict[str, Any]:
        return self._schemas.get(f"{org_id}:{schema_name}", {})
    def list_schemas(self, org_id: str) -> List[Dict[str, Any]]:
        return [s for s in self._schemas.values() if s["org_id"] == org_id]
    def drop_schema(self, org_id: str, schema_name: str) -> bool:
        key = f"{org_id}:{schema_name}"
        if key in self._schemas:
            del self._schemas[key]
            return True
        return False
    def get_tables(self, org_id: str, schema_name: str) -> List[str]:
        schema = self.get_schema(org_id, schema_name)
        return list(schema.get("tables", []))
