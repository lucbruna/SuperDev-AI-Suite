from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class GitHubReleases(BaseTool):
    """Manage GitHub releases."""

    _name = "github_releases"
    _description = "Manage GitHub releases: list, get, create, delete"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._releases: list[dict[str, Any]] = []

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
                return {"success": True, "releases": self._releases, "count": len(self._releases)}
            elif action == "get":
                tag = params.get("tag", "")
                release = next((r for r in self._releases if r.get("tag") == tag), None)
                if not release:
                    return {"success": False, "error": f"Release not found: {tag}"}
                return {"success": True, "release": release}
            elif action == "create":
                release = {
                    "tag": params.get("tag", ""),
                    "name": params.get("name", ""),
                    "body": params.get("body", ""),
                    "draft": params.get("draft", False),
                    "prerelease": params.get("prerelease", False),
                    "created_at": "2024-01-01T00:00:00Z",
                }
                self._releases.append(release)
                return {"success": True, "release": release}
            elif action == "delete":
                tag = params.get("tag", "")
                self._releases = [r for r in self._releases if r.get("tag") != tag]
                return {"success": True, "message": f"Deleted release {tag}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._releases.clear()

    async def cleanup(self) -> None:
        self._releases.clear()
