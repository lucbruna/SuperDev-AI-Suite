from __future__ import annotations

import os
import platform
from typing import Any


class TelemetryContext:
    """Provides contextual metadata for telemetry events."""

    def __init__(self) -> None:
        self._tags: dict[str, str] = {
            "host": platform.node(),
            "platform": platform.system(),
            "pid": str(os.getpid()),
        }

    def set_tag(self, key: str, value: str) -> None:
        self._tags[key] = value

    def get_context(self) -> dict[str, str]:
        return dict(self._tags)
