from __future__ import annotations

from typing import Any


class ArchitectureReview:
    """Review workflow for architecture submissions with approval/rejection."""

    def __init__(self) -> None:
        self._reviews: dict[str, dict[str, Any]] = {}

    def submit(
        self,
        review_id: str,
        title: str,
        content: str,
        reviewers: list[str],
    ) -> str:
        entry: dict[str, Any] = {
            "id": review_id,
            "title": title,
            "content": content,
            "reviewers": reviewers,
            "status": "pending",
            "votes": {},
            "comments": [],
        }
        self._reviews[review_id] = entry
        return review_id

    def approve(self, review_id: str, reviewer: str, comments: str = "") -> bool:
        review = self._reviews.get(review_id)
        if not review or review["status"] != "pending":
            return False
        review["votes"][reviewer] = "approve"
        review["comments"].append({"reviewer": reviewer, "comment": comments})
        if len(review["votes"]) >= len(review["reviewers"]):
            review["status"] = "approved"
        return True

    def reject(self, review_id: str, reviewer: str, reason: str) -> bool:
        review = self._reviews.get(review_id)
        if not review or review["status"] != "pending":
            return False
        review["votes"][reviewer] = "reject"
        review["comments"].append({"reviewer": reviewer, "comment": reason})
        review["status"] = "rejected"
        return True

    def get_review(self, review_id: str) -> dict[str, Any] | None:
        return self._reviews.get(review_id)

    @property
    def pending_count(self) -> int:
        return sum(1 for r in self._reviews.values() if r["status"] == "pending")

    def to_dict(self) -> dict[str, Any]:
        return {
            "reviews": self._reviews,
            "pending_count": self.pending_count,
        }
