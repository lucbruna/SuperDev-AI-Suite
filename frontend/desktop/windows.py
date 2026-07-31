from __future__ import annotations

import logging
from typing import Any


class WindowsAdapter:
    """Windows desktop platform adapter."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.desktop.windows")

    def capabilities(self) -> dict[str, Any]:
        return {
            "platform": "windows",
            "native_shell": True,
            "tray": True,
            "shortcuts": True,
            "auto_update": True,
        }
