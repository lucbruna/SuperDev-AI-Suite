from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class GitHubActions(BaseTool):
    """Manage GitHub Actions workflows."""

    _name = "github_actions"
    _description = "Manage GitHub Actions workflows: list, trigger, runs, cancel"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._workflows: list[dict[str, Any]] = []
        self._runs: list[dict[str, Any]] = []

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
            if action == "list_workflows":
                return {"success": True, "workflows": self._workflows, "count": len(self._workflows)}
            elif action == "trigger":
                workflow_id = params.get("workflow_id", "")
                ref = params.get("ref", "main")
                run = {
                    "id": len(self._runs) + 1,
                    "workflow_id": workflow_id,
                    "ref": ref,
                    "status": "queued",
                    "created_at": "2024-01-01T00:00:00Z",
                }
                self._runs.append(run)
                return {"success": True, "run": run}
            elif action == "list_runs":
                return {"success": True, "runs": self._runs, "count": len(self._runs)}
            elif action == "get_run":
                run_id = params.get("run_id")
                run = next((r for r in self._runs if r.get("id") == run_id), None)
                if not run:
                    return {"success": False, "error": f"Run not found: {run_id}"}
                return {"success": True, "run": run}
            elif action == "cancel_run":
                run_id = params.get("run_id")
                for run in self._runs:
                    if run.get("id") == run_id:
                        run["status"] = "cancelled"
                        return {"success": True, "run": run}
                return {"success": False, "error": f"Run not found: {run_id}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._workflows.clear()
        self._runs.clear()

    async def cleanup(self) -> None:
        self._workflows.clear()
        self._runs.clear()
