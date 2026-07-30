from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Milestones:
    """GitHub milestone management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self, state: str = "open", **params: Any) -> list[dict[str, Any]]:
        data = self._client.get(
            f"/repos/{self._client.owner}/{self._client.repo}/milestones",
            params={"state": state, **params},
        )
        return data.get("data", [])

    def get(self, milestone_number: int) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/milestones/{milestone_number}")

    def create(self, title: str, description: str = "", due_on: str = "") -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/milestones",
            json={"title": title, "description": description, "due_on": due_on},
        )

    def update(self, milestone_number: int, **kwargs: Any) -> dict[str, Any]:
        return self._client.patch(
            f"/repos/{self._client.owner}/{self._client.repo}/milestones/{milestone_number}",
            json=kwargs,
        )

    def delete(self, milestone_number: int) -> dict[str, Any]:
        return self._client.delete(f"/repos/{self._client.owner}/{self._client.repo}/milestones/{milestone_number}")
