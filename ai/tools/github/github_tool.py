from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .repository import GitHubRepository
from .issues import GitHubIssues
from .pull_requests import GitHubPullRequests
from .actions import GitHubActions
from .releases import GitHubReleases


class GitHubTool(BaseTool):
    """Composite GitHub tool for repository operations."""

    _name = "github"
    _description = "GitHub API operations: repos, issues, PRs, actions, releases"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._repo = GitHubRepository()
        self._issues = GitHubIssues()
        self._prs = GitHubPullRequests()
        self._actions = GitHubActions()
        self._releases = GitHubReleases()

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

        if sub_tool == "repo" or action in ("list", "get", "create", "delete", "search"):
            return await self._repo.execute(params)
        elif sub_tool == "issues" or action in ("list_issues", "create_issue", "close_issue"):
            return await self._issues.execute(params)
        elif sub_tool == "pull_requests":
            return await self._prs.execute(params)
        elif sub_tool == "actions":
            return await self._actions.execute(params)
        elif sub_tool == "releases":
            return await self._releases.execute(params)
        return {"success": False, "error": f"Unknown GitHub action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        for tool in (self._repo, self._issues, self._prs, self._actions, self._releases):
            await tool.cleanup()
