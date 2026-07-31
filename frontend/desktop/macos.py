from __future__ import annotations

import logging
from typing import Any


class MacOSAdapter:
    """macOS desktop platform adapter."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.desktop.macos")

    def capabilities(self) -> dict[str, Any]:
        return {
            "platform": "macos",
            "native_shell": True,
            "tray": True,
            "shortcuts": True,
            "auto_update": True,
        }
