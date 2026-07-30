from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Issues:
    """GitHub issue management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self, state: str = "open", **params: Any) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/issues", params={"state": state, **params})
        return data.get("data", [])

    def get(self, issue_number: int) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/issues/{issue_number}")

    def create(self, title: str, body: str = "", labels: list[str] | None = None) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/issues",
            json={"title": title, "body": body, "labels": labels or []},
        )

    def update(self, issue_number: int, **kwargs: Any) -> dict[str, Any]:
        return self._client.patch(f"/repos/{self._client.owner}/{self._client.repo}/issues/{issue_number}", json=kwargs)

    def close(self, issue_number: int) -> dict[str, Any]:
        return self.update(issue_number, state="closed")

    def search(self, query: str) -> list[dict[str, Any]]:
        data = self._client.get("/search/issues", params={"q": query})
        return data.get("data", [])

    def list_comments(self, issue_number: int) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/issues/{issue_number}/comments")
        return data.get("data", [])

    def create_comment(self, issue_number: int, body: str) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/issues/{issue_number}/comments",
            json={"body": body},
        )
