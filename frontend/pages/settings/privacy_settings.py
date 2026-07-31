from __future__ import annotations

import json
import logging
from typing import Any


class PrivacySettings:
    """Data export, deletion and privacy preferences."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.settings.privacy")
        self._preferences: dict[str, Any] = {}

    def render(self) -> dict[str, Any]:
        return {"preferences": self.preferences()}

    def export_data(self) -> str:
        return json.dumps({"preferences": self._preferences}, indent=2, default=str)

    def delete_data(self) -> bool:
        self._preferences.clear()
        return True

    def preferences(self) -> dict[str, Any]:
        return dict(self._preferences)
