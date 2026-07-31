"""Analyzer for database schemas and performance."""
from typing import List, Dict, Any
from .models import DatabaseSchema, Table, Column


class DatabaseAnalyzer:
    """Analyzes database schemas for metrics and optimization."""

    def analyze_schema(self, schema: DatabaseSchema) -> Dict[str, Any]:
        tables = schema.tables
        total_columns = sum(len(t.columns) for t in tables)
        total_indexes = sum(len(t.indexes) for t in tables)
        total_fks = sum(len(t.foreign_keys) for t in tables)

        pk_count = sum(1 for t in tables for c in t.columns if c.primary_key)
        nullable_count = sum(1 for t in tables for c in t.columns if c.nullable)

        return {
            "schema_name": schema.name,
            "total_tables": len(tables),
            "total_columns": total_columns,
            "total_indexes": total_indexes,
            "total_foreign_keys": total_fks,
            "primary_keys": pk_count,
            "nullable_columns": nullable_count,
            "avg_columns_per_table": total_columns / len(tables) if tables else 0,
        }

    def analyze_table(self, table: Table) -> Dict[str, Any]:
        return {
            "table_name": table.name,
            "columns": len(table.columns),
            "indexes": len(table.indexes),
            "foreign_keys": len(table.foreign_keys),
            "nullable_ratio": sum(1 for c in table.columns if c.nullable) / len(table.columns) if table.columns else 0,
        }

    def find_unused_indexes(self, schema: DatabaseSchema) -> List[str]:
        """Find tables with many indexes but few foreign keys."""
        unused = []
        for table in schema.tables:
            if len(table.indexes) > 3 and len(table.foreign_keys) == 0:
                unused.append(table.name)
        return unused

    def suggest_optimizations(self, schema: DatabaseSchema) -> List[Dict[str, str]]:
        suggestions = []
        for table in schema.tables:
            if len(table.columns) > 20:
                suggestions.append({"table": table.name, "suggestion": "Consider normalizing - too many columns"})
            if not any(c.primary_key for c in table.columns):
                suggestions.append({"table": table.name, "suggestion": "Add a primary key"})
            if len(table.indexes) == 0 and len(table.columns) > 3:
                suggestions.append({"table": table.name, "suggestion": "Consider adding indexes"})
        return suggestions
