from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .connection import DatabaseConnection
from .query import DatabaseQuery
from .migration import DatabaseMigration
from .schema import DatabaseSchema
from .backup import DatabaseBackup


class DatabaseTool(BaseTool):
    """Composite database tool for data operations."""

    _name = "database"
    _description = "Database operations: connection, query, migration, schema, backup"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._connection = DatabaseConnection()
        self._query = DatabaseQuery()
        self._migration = DatabaseMigration()
        self._schema = DatabaseSchema()
        self._backup = DatabaseBackup()

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        sub_tool = params.get("sub_tool", "")
        action = params.get("action", "")

        if sub_tool == "connection" or action in ("connect", "disconnect", "ping"):
            return await self._connection.execute(params)
        elif sub_tool == "query":
            return await self._query.execute(params)
        elif sub_tool == "migration":
            return await self._migration.execute(params)
        elif sub_tool == "schema":
            return await self._schema.execute(params)
        elif sub_tool == "backup":
            return await self._backup.execute(params)
        return {"success": False, "error": f"Unknown database action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        for tool in (self._connection, self._query, self._migration, self._schema, self._backup):
            await tool.cleanup()
