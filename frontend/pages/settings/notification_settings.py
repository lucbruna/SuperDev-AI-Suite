from __future__ import annotations

import logging
from typing import Any


class NotificationSettings:
    """Notification channel preferences."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.settings.notifications")
        self._channels: dict[str, bool] = {
            "email": True,
            "push": True,
            "desktop": False,
            "sms": False,
        }

    def render(self) -> dict[str, Any]:
        return {"channels": self.channels(), "enabled": sum(self._channels.values())}

    def channels(self) -> list[dict[str, Any]]:
        return [
            {"channel": channel, "enabled": enabled}
            for channel, enabled in self._channels.items()
        ]

    def update(self, data: dict[str, Any]) -> bool:
        self._channels.update(data)
        return True

    def test(self, channel: str) -> bool:
        return channel in self._channels
