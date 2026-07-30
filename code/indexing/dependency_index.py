from __future__ import annotations

import logging
from typing import Any


class DependencyIndex:
    """Indexes dependency relationships between modules."""

    def __init__(self) -> None:
        self._deps: dict[str, list[str]] = {}
        self._log = logging.getLogger("superdev.code.indexing.deps")

    def add(self, module: str, depends_on: str) -> None:
        self._deps.setdefault(module, []).append(depends_on)

    def get(self, module: str) -> list[str]:
        return self._deps.get(module, [])
