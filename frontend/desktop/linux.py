from __future__ import annotations

import logging
from typing import Any


class LinuxAdapter:
    """Linux desktop platform adapter."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.desktop.linux")

    def capabilities(self) -> dict[str, Any]:
        return {
            "platform": "linux",
            "native_shell": True,
            "tray": True,
            "shortcuts": True,
            "auto_update": False,
        }
