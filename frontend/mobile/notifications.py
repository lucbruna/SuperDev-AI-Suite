from __future__ import annotations

import logging
import time
from typing import Any


class MobileNotifications:
    """Manages push/local notifications on mobile surfaces."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.mobile.notifications")
        self._enabled = True
        self._history: list[dict[str, Any]] = []
        self._token: str | None = None

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled

    def set_token(self, token: str) -> None:
        self._token = token

    def send(self, title: str, body: str, data: dict[str, Any] | None = None) -> str:
        notification = {
            "id": f"n{len(self._history) + 1}",
            "title": title,
            "body": body,
            "data": data or {},
            "ts": time.time(),
            "delivered": self._enabled,
        }
        self._history.append(notification)
        return notification["id"]

    def history(self, limit: int | None = None) -> list[dict[str, Any]]:
        items = list(self._history)
        return items[-limit:] if limit is not None else items

    def clear(self) -> None:
        self._history.clear()

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "token": self._token,
            "sent": len(self._history),
        }
