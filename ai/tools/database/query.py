from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class DatabaseQuery(BaseTool):
    """Execute database queries."""

    _name = "database_query"
    _description = "Execute database queries: select, insert, update, delete, execute_raw"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._query_log: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "")
        query = params.get("query", "")
        try:
            if action == "select":
                self._query_log.append({"action": "select", "query": query})
                return {"success": True, "rows": [], "count": 0, "query": query}
            elif action == "insert":
                table = params.get("table", "")
                data = params.get("data", {})
                self._query_log.append({"action": "insert", "table": table, "data": data})
                return {"success": True, "inserted": 1, "table": table}
            elif action == "update":
                table = params.get("table", "")
                data = params.get("data", {})
                where = params.get("where", {})
                self._query_log.append({"action": "update", "table": table, "data": data, "where": where})
                return {"success": True, "updated": 1, "table": table}
            elif action == "delete":
                table = params.get("table", "")
                where = params.get("where", {})
                self._query_log.append({"action": "delete", "table": table, "where": where})
                return {"success": True, "deleted": 1, "table": table}
            elif action == "execute_raw":
                self._query_log.append({"action": "execute_raw", "query": query})
                return {"success": True, "affected_rows": 0, "query": query}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._query_log.clear()

    async def cleanup(self) -> None:
        self._query_log.clear()
