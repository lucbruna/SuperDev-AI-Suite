"""Manager for database connections and operations."""
from typing import List, Dict, Any, Optional
from .models import DatabaseConnection, DatabaseSchema


class DatabaseManager:
    """Manages database connections and provides unified access."""

    def __init__(self):
        self._connections: Dict[str, DatabaseConnection] = {}
        self._schemas: Dict[str, DatabaseSchema] = {}

    def add_connection(self, conn: DatabaseConnection) -> str:
        self._connections[conn.connection_id] = conn
        return conn.connection_id

    def get_connection(self, connection_id: str) -> Optional[DatabaseConnection]:
        return self._connections.get(connection_id)

    def remove_connection(self, connection_id: str) -> bool:
        if connection_id in self._connections:
            del self._connections[connection_id]
            return True
        return False

    def register_schema(self, schema: DatabaseSchema) -> None:
        self._schemas[schema.schema_id] = schema

    def get_schema(self, schema_id: str) -> Optional[DatabaseSchema]:
        return self._schemas.get(schema_id)

    def list_connections(self) -> List[DatabaseConnection]:
        return list(self._connections.values())

    def list_schemas(self) -> List[DatabaseSchema]:
        return list(self._schemas.values())

    def get_stats(self) -> Dict[str, Any]:
        return {
            "connections": len(self._connections),
            "schemas": len(self._schemas),
        }
