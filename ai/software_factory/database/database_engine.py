"""Core engine for database operations."""
from typing import Any

from .migration_manager import MigrationManager
from .models import DatabaseConnection, DatabaseSchema, Migration
from .query_builder import QueryBuilder
from .schema_designer import SchemaDesigner


class DatabaseEngine:
    """Central engine coordinating database operations."""

    def __init__(self):
        self.schema_designer = SchemaDesigner()
        self.migration_manager = MigrationManager()
        self.query_builder = QueryBuilder()
        self._schemas: dict[str, DatabaseSchema] = {}
        self._connections: dict[str, DatabaseConnection] = {}
        self._migrations: list[Migration] = []

    def register_schema(self, schema: DatabaseSchema) -> str:
        self._schemas[schema.schema_id] = schema
        return schema.schema_id

    def register_connection(self, conn: DatabaseConnection) -> str:
        self._connections[conn.connection_id] = conn
        return conn.connection_id

    def get_schema(self, schema_id: str) -> DatabaseSchema | None:
        return self._schemas.get(schema_id)

    def create_migration(self, name: str, steps: list[dict[str, Any]]) -> Migration:
        from .models import MigrationStep
        migration_steps = [
            MigrationStep(operation=s.get("operation", ""), table_name=s.get("table", ""), sql=s.get("sql", ""))
            for s in steps
        ]
        migration = Migration(name=name, steps=migration_steps, version=f"{len(self._migrations)+1}.0.0")
        self._migrations.append(migration)
        return migration

    def get_migrations(self) -> list[Migration]:
        return list(self._migrations)

    def get_stats(self) -> dict[str, Any]:
        return {
            "schemas": len(self._schemas),
            "connections": len(self._connections),
            "migrations": len(self._migrations),
        }
