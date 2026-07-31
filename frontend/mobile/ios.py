from __future__ import annotations

import logging
from typing import Any


class iOSAdapter:
    """iOS platform adapter for the mobile surface."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.mobile.ios")

    def capabilities(self) -> dict[str, Any]:
        return {
            "platform": "ios",
            "notifications": True,
            "background_sync": True,
            "biometric_auth": True,
        }

    def push_token(self) -> str:
        return "ios-push-token"
