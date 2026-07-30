from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class GitHubPullRequests(BaseTool):
    """Manage GitHub pull requests."""

    _name = "github_pull_requests"
    _description = "Manage GitHub pull requests: list, get, create, merge, update"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._prs: list[dict[str, Any]] = []

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
                return {"success": True, "pull_requests": self._prs, "count": len(self._prs)}
            elif action == "get":
                pr_id = params.get("pr_id")
                pr = next((p for p in self._prs if p.get("id") == pr_id), None)
                if not pr:
                    return {"success": False, "error": f"PR not found: {pr_id}"}
                return {"success": True, "pull_request": pr}
            elif action == "create":
                pr = {
                    "id": len(self._prs) + 1,
                    "title": params.get("title", ""),
                    "body": params.get("body", ""),
                    "head": params.get("head", ""),
                    "base": params.get("base", "main"),
                    "state": "open",
                }
                self._prs.append(pr)
                return {"success": True, "pull_request": pr}
            elif action == "merge":
                pr_id = params.get("pr_id")
                for pr in self._prs:
                    if pr.get("id") == pr_id:
                        pr["state"] = "merged"
                        return {"success": True, "pull_request": pr}
                return {"success": False, "error": f"PR not found: {pr_id}"}
            elif action == "update":
                pr_id = params.get("pr_id")
                for pr in self._prs:
                    if pr.get("id") == pr_id:
                        if "title" in params:
                            pr["title"] = params["title"]
                        if "body" in params:
                            pr["body"] = params["body"]
                        return {"success": True, "pull_request": pr}
                return {"success": False, "error": f"PR not found: {pr_id}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._prs.clear()

    async def cleanup(self) -> None:
        self._prs.clear()
