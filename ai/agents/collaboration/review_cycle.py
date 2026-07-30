from __future__ import annotations

from typing import Any, Dict, List, Optional


class ReviewCycle:
    """Review cycle for collaborative work."""

    def __init__(self) -> None:
        self._reviews: Dict[str, Dict[str, Any]] = {}

    def start_review(self, review_id: str, item: str, reviewers: List[str]) -> None:
        self._reviews[review_id] = {"item": item, "reviewers": reviewers, "comments": [], "approved": False}

    def add_comment(self, review_id: str, reviewer: str, comment: str) -> bool:
        review = self._reviews.get(review_id)
        if review and reviewer in review["reviewers"]:
            review["comments"].append({"reviewer": reviewer, "comment": comment})
            return True
        return False

    def approve(self, review_id: str) -> bool:
        review = self._reviews.get(review_id)
        if review:
            review["approved"] = True
            return True
        return False

    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        review = self._reviews.get(review_id)
        return dict(review) if review else None

    def clear(self) -> None:
        self._reviews.clear()
