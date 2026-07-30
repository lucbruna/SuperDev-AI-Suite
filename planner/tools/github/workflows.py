from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Workflows:
    """GitHub Actions workflow management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/actions/workflows")
        return data.get("data", [])

    def get(self, workflow_id: str) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/actions/workflows/{workflow_id}")

    def trigger(self, workflow_id: str, ref: str = "main", inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/actions/workflows/{workflow_id}/dispatches",
            json={"ref": ref, "inputs": inputs or {}},
        )

    def cancel(self, run_id: int) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/actions/runs/{run_id}/cancel"
        )

    def list_runs(self, workflow_id: str | None = None, **params: Any) -> list[dict[str, Any]]:
        path = f"/repos/{self._client.owner}/{self._client.repo}/actions/runs"
        if workflow_id:
            path = f"/repos/{self._client.owner}/{self._client.repo}/actions/workflows/{workflow_id}/runs"
        data = self._client.get(path, params=params)
        return data.get("data", [])

    def get_run(self, run_id: int) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/actions/runs/{run_id}")
