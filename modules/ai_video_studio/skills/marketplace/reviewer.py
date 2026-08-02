"""Market reviewer — approves or rejects marketplace submissions."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.marketplace.publisher import MarketPublisher


class MarketReviewer:
    """Review gate over the publisher's submissions."""

    def __init__(self, publisher: MarketPublisher | None = None) -> None:
        self._publisher = publisher or MarketPublisher()

    def approve(self, skill_id: str) -> dict[str, Any]:
        return self._publisher.approve(skill_id)

    def reject(self, skill_id: str, *, reason: str = "not reviewed") -> dict[str, Any]:
        return self._publisher.reject(skill_id, reason=reason)

    def pending(self) -> list[dict[str, Any]]:
        return self._publisher.list(status="submitted")
