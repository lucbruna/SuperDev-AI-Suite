from __future__ import annotations

import logging
from typing import Any


class FrameworkRegistry:
    """Registry of supported frameworks."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks")
        self._frameworks: dict[str, dict[str, Any]] = {}

    def register(self, name: str, config: dict[str, Any]) -> None:
        self._frameworks[name] = config
        self._log.info("Registered framework: %s", name)

    def get(self, name: str) -> dict[str, Any] | None:
        return self._frameworks.get(name)

    def list_frameworks(self) -> list[str]:
        return list(self._frameworks.keys())
