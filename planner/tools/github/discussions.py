from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Discussions:
    """GitHub Discussions management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self, category_id: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if category_id:
            params["category_id"] = category_id
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/discussions", params=params)
        return data.get("data", [])

    def get(self, discussion_number: int) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/discussions/{discussion_number}")

    def create(self, title: str, body: str, category_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/discussions",
            json={"title": title, "body": body, "category_id": category_id},
        )

    def update(self, discussion_number: int, **kwargs: Any) -> dict[str, Any]:
        return self._client.patch(
            f"/repos/{self._client.owner}/{self._client.repo}/discussions/{discussion_number}",
            json=kwargs,
        )

    def delete(self, discussion_number: int) -> dict[str, Any]:
        return self._client.delete(f"/repos/{self._client.owner}/{self._client.repo}/discussions/{discussion_number}")

    def list_comments(self, discussion_number: int) -> list[dict[str, Any]]:
        data = self._client.get(
            f"/repos/{self._client.owner}/{self._client.repo}/discussions/{discussion_number}/comments"
        )
        return data.get("data", [])

    def create_comment(self, discussion_number: int, body: str) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/discussions/{discussion_number}/comments",
            json={"body": body},
        )
