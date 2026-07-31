from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class ProfileEngine:
    """Renders the user profile page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.profile")
        self._context = context or FrontendContext()
        self._profile: dict[str, Any] = {"name": "", "email": "", "bio": ""}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "profile",
            "profile": dict(self._profile),
        }

    def update(self, data: dict[str, Any]) -> bool:
        self._profile.update(data)
        return True

    def change_password(self, current: str, new: str) -> bool:
        if not current or len(new) < 8:
            return False
        return True

    def activity(self) -> list[dict[str, Any]]:
        return [{"ts": time.time(), "event": "profile_updated"}]
