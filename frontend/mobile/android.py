from __future__ import annotations

import logging
from typing import Any


class AndroidAdapter:
    """Android platform adapter for the mobile surface."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.mobile.android")

    def capabilities(self) -> dict[str, Any]:
        return {
            "platform": "android",
            "notifications": True,
            "background_sync": True,
            "biometric_auth": True,
        }

    def push_token(self) -> str:
        return "android-push-token"
