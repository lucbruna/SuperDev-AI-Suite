from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class CodeReview:
    """GitHub pull request code review operations."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def create_review(self, pr_number: int, body: str, event: str = "COMMENT", comments: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}/reviews",
            json={"body": body, "event": event, "comments": comments or []},
        )

    def list_reviews(self, pr_number: int) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}/reviews")
        return data.get("data", [])

    def submit_review(self, pr_number: int, review_id: int, body: str, event: str = "COMMENT") -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}/reviews/{review_id}/events",
            json={"body": body, "event": event},
        )

    def dismiss_review(self, pr_number: int, review_id: int, message: str = "") -> dict[str, Any]:
        return self._client.put(
            f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}/reviews/{review_id}/dismissals",
            json={"message": message},
        )

    def list_comments(self, pr_number: int) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}/comments")
        return data.get("data", [])
