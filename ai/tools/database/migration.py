from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class DatabaseMigration(BaseTool):
    """Manage database migrations."""

    _name = "database_migration"
    _description = "Manage database migrations: create, run, rollback, list, status"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._migrations: list[dict[str, Any]] = []
        self._applied: list[str] = []

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
        try:
            if action == "create":
                name = params.get("name", f"migration_{len(self._migrations) + 1}")
                migration = {"name": name, "up": params.get("up", ""), "down": params.get("down", "")}
                self._migrations.append(migration)
                return {"success": True, "migration": migration}
            elif action == "run":
                migration_id = params.get("migration_id", "")
                if migration_id:
                    self._applied.append(migration_id)
                return {"success": True, "message": f"Applied migration {migration_id}"}
            elif action == "rollback":
                migration_id = params.get("migration_id", "")
                self._applied = [m for m in self._applied if m != migration_id]
                return {"success": True, "message": f"Rolled back migration {migration_id}"}
            elif action == "list":
                return {"success": True, "migrations": self._migrations, "count": len(self._migrations)}
            elif action == "status":
                return {"success": True, "applied": self._applied, "pending": [m["name"] for m in self._migrations if m["name"] not in self._applied]}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._applied.clear()

    async def cleanup(self) -> None:
        self._migrations.clear()
        self._applied.clear()
