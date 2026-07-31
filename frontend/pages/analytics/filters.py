from __future__ import annotations

import logging
from typing import Any


class AnalyticsFilters:
    """Query filters for analytics views."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.analytics.filters")
        self._active: dict[str, Any] = {}

    def render(self) -> dict[str, Any]:
        return {"active": dict(self._active)}

    def apply(self, filters: dict[str, Any]) -> str:
        self._active.update(filters)
        return "filters-updated"

    def reset(self) -> None:
        self._active.clear()
