from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .branch import GitBranch
from .commit import GitCommit
from .diff import GitDiff
from .history import GitHistory
from .merge import GitMerge
from .repository import GitRepository
from .stash import GitStash


class GitTool(BaseTool):
    """Composite Git tool for repository operations."""

    _name = "git"
    _description = "Complete Git operations: repo, branch, commit, diff, merge, history, stash"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._repo = GitRepository()
        self._branch = GitBranch()
        self._commit = GitCommit()
        self._diff = GitDiff()
        self._merge = GitMerge()
        self._history = GitHistory()
        self._stash = GitStash()

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
        sub_tool = params.get("sub_tool", "")
        sub_action = params.get("action", "")

        if sub_tool == "repo" or sub_action in ("init", "clone", "status", "log"):
            return await self._repo.execute(params)
        elif sub_tool == "branch" or sub_action in ("list", "create", "delete", "switch"):
            return await self._branch.execute(params)
        elif sub_tool == "commit":
            return await self._commit.execute(params)
        elif sub_tool == "diff":
            return await self._diff.execute(params)
        elif sub_tool == "merge":
            return await self._merge.execute(params)
        elif sub_tool == "history":
            return await self._history.execute(params)
        elif sub_tool == "stash" or sub_action in ("push", "pop"):
            return await self._stash.execute(params)
        return {"success": False, "error": f"Unknown git action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        for tool in (self._repo, self._branch, self._commit, self._diff, self._merge, self._history, self._stash):
            await tool.cleanup()
