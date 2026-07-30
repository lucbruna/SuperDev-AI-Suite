from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Permissions:
    """GitHub repository permissions management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def get_collaborator_permission(self, username: str) -> dict[str, Any]:
        return self._client.get(
            f"/repos/{self._client.owner}/{self._client.repo}/collaborators/{username}/permission"
        )

    def add_collaborator(self, username: str, permission: str = "push") -> dict[str, Any]:
        return self._client.put(
            f"/repos/{self._client.owner}/{self._client.repo}/collaborators/{username}",
            json={"permission": permission},
        )

    def remove_collaborator(self, username: str) -> dict[str, Any]:
        return self._client.delete(
            f"/repos/{self._client.owner}/{self._client.repo}/collaborators/{username}"
        )

    def list_collaborators(self, affiliation: str = "all") -> list[dict[str, Any]]:
        data = self._client.get(
            f"/repos/{self._client.owner}/{self._client.repo}/collaborators",
            params={"affiliation": affiliation},
        )
        return data.get("data", [])

    def check_collaborator(self, username: str) -> bool:
        resp = self._client.get(
            f"/repos/{self._client.owner}/{self._client.repo}/collaborators/{username}"
        )
        return resp.get("status") == 204

    def get_team_permissions(self, team_slug: str) -> dict[str, Any]:
        return self._client.get(
            f"/orgs/{self._client.owner}/teams/{team_slug}/repos/{self._client.repo}"
        )

    def add_team(self, team_slug: str, permission: str = "push") -> dict[str, Any]:
        return self._client.put(
            f"/orgs/{self._client.owner}/teams/{team_slug}/repos/{self._client.owner}/{self._client.repo}",
            json={"permission": permission},
        )

    def remove_team(self, team_slug: str) -> dict[str, Any]:
        return self._client.delete(
            f"/orgs/{self._client.owner}/teams/{team_slug}/repos/{self._client.owner}/{self._client.repo}"
        )
