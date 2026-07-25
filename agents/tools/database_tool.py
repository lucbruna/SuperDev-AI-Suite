from __future__ import annotations

from typing import Any, Optional

from ..base.base_tool import BaseTool


class DatabaseTool(BaseTool):
    _name = "database"
    _description = "Execute SQL queries against a database"
    _permissions = ["read", "write"]

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "query" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        connection_string = params.get("connection_string", "")
        query = params.get("query", "")
        query_params = params.get("params", [])

        if not query:
            return {"success": False, "error": "No SQL query provided"}

        try:
            if "sqlite" in connection_string or not connection_string:
                return await self._execute_sqlite(connection_string, query, query_params)
            elif "postgres" in connection_string or "postgresql" in connection_string:
                return await self._execute_postgres(connection_string, query, query_params)
            else:
                return {"success": False, "error": f"Unsupported database: {connection_string}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_sqlite(self, conn_str: str, query: str, params: list) -> dict[str, Any]:
        import sqlite3
        db_path = conn_str.replace("sqlite:///", "") if conn_str else ":memory:"
        conn = sqlite3.connect(db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            if query.strip().upper().startswith(("SELECT", "PRAGMA")):
                rows = [dict(row) for row in cursor.fetchall()]
                return {"success": True, "results": rows, "row_count": len(rows)}
            else:
                conn.commit()
                return {"success": True, "affected_rows": cursor.rowcount}
        finally:
            conn.close()

    async def _execute_postgres(self, conn_str: str, query: str, params: list) -> dict[str, Any]:
        try:
            import asyncpg
            conn = await asyncpg.connect(conn_str)
            try:
                if query.strip().upper().startswith("SELECT"):
                    rows = await conn.fetch(query, *params)
                    return {"success": True, "results": [dict(r) for r in rows], "row_count": len(rows)}
                else:
                    result = await conn.execute(query, *params)
                    return {"success": True, "affected": result}
            finally:
                await conn.close()
        except ImportError:
            return {"success": False, "error": "asyncpg not installed. Install with: pip install asyncpg"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
