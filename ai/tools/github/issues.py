from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class GitHubIssues(BaseTool):
    """Manage GitHub issues."""

    _name = "github_issues"
    _description = "Manage GitHub issues: list, get, create, update, close"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._issues: list[dict[str, Any]] = []

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
                return {"success": True, "issues": self._issues, "count": len(self._issues)}
            elif action == "get":
                issue_id = params.get("issue_id")
                issue = next((i for i in self._issues if i.get("id") == issue_id), None)
                if not issue:
                    return {"success": False, "error": f"Issue not found: {issue_id}"}
                return {"success": True, "issue": issue}
            elif action == "create":
                issue = {
                    "id": len(self._issues) + 1,
                    "title": params.get("title", ""),
                    "body": params.get("body", ""),
                    "labels": params.get("labels", []),
                    "state": "open",
                }
                self._issues.append(issue)
                return {"success": True, "issue": issue}
            elif action == "update":
                issue_id = params.get("issue_id")
                for issue in self._issues:
                    if issue.get("id") == issue_id:
                        if "title" in params:
                            issue["title"] = params["title"]
                        if "body" in params:
                            issue["body"] = params["body"]
                        return {"success": True, "issue": issue}
                return {"success": False, "error": f"Issue not found: {issue_id}"}
            elif action == "close":
                issue_id = params.get("issue_id")
                for issue in self._issues:
                    if issue.get("id") == issue_id:
                        issue["state"] = "closed"
                        return {"success": True, "issue": issue}
                return {"success": False, "error": f"Issue not found: {issue_id}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._issues.clear()

    async def cleanup(self) -> None:
        self._issues.clear()
