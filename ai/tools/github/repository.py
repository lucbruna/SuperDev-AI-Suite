from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class GitHubRepository(BaseTool):
    """Manage GitHub repositories."""

    _name = "github_repository"
    _description = "Manage GitHub repositories: list, get, create, delete, search"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._repos: list[dict[str, Any]] = []

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
            if action == "list":
                return {"success": True, "repositories": self._repos, "count": len(self._repos)}
            elif action == "get":
                name = params.get("name", "")
                repo = next((r for r in self._repos if r.get("name") == name), None)
                if not repo:
                    return {"success": False, "error": f"Repository not found: {name}"}
                return {"success": True, "repository": repo}
            elif action == "create":
                repo = {
                    "name": params.get("name", ""),
                    "description": params.get("description", ""),
                    "private": params.get("private", False),
                    "created_at": "2024-01-01T00:00:00Z",
                }
                self._repos.append(repo)
                return {"success": True, "repository": repo}
            elif action == "delete":
                name = params.get("name", "")
                self._repos = [r for r in self._repos if r.get("name") != name]
                return {"success": True, "message": f"Deleted {name}"}
            elif action == "search":
                query = params.get("query", "").lower()
                results = [r for r in self._repos if query in r.get("name", "").lower()]
                return {"success": True, "repositories": results, "count": len(results)}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._repos.clear()

    async def cleanup(self) -> None:
        self._repos.clear()
