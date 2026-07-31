from __future__ import annotations

import logging
from typing import Any

from .notifications import MobileNotifications
from .offline import OfflineCache
from .synchronization import SynchronizationEngine


class MobileEngine:
    """Coordinates the mobile surface: platforms, offline, sync and notifications."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.mobile")
        self._platforms: dict[str, dict[str, Any]] = {}
        self._active = "android"
        self.notifications = MobileNotifications()
        self.offline = OfflineCache()
        self.sync = SynchronizationEngine()

    def register_platform(self, name: str, config: dict[str, Any]) -> None:
        self._platforms[name] = {"name": name, **config}

    def set_active(self, name: str) -> bool:
        if name not in self._platforms:
            return False
        self._active = name
        return True

    def active(self) -> str:
        return self._active

    def platforms(self) -> list[str]:
        return list(self._platforms)

    def render(self) -> dict[str, Any]:
        return {
            "surface": "mobile",
            "active": self._active,
            "platforms": self.platforms(),
            "offline": self.offline.status(),
            "sync": self.sync.status(),
            "notifications": self.notifications.status(),
        }
