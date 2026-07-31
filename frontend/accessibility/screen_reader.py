from __future__ import annotations

from typing import Any


class ScreenReader:
    """Manages screen-reader announcements."""

    def __init__(self) -> None:
        self._live_regions: dict[str, str] = {}
        self._announcements: list[str] = []
        self._enabled = True

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled

    def announce(self, message: str, polite: bool = True) -> None:
        if not self._enabled:
            return
        region = "polite" if polite else "assertive"
        self._live_regions[region] = message
        self._announcements.append(message)

    def set_region(self, region: str, content: str) -> None:
        self._live_regions[region] = content

    def get_region(self, region: str) -> str:
        return self._live_regions.get(region, "")

    def history(self, limit: int | None = None) -> list[str]:
        messages = list(self._announcements)
        if limit is not None:
            messages = messages[-limit:]
        return messages

    def clear(self) -> None:
        self._announcements.clear()

    def status(self) -> dict[str, Any]:
        return {"enabled": self._enabled, "regions": dict(self._live_regions)}
