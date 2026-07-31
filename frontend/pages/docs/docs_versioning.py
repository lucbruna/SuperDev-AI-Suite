from __future__ import annotations

import logging
from typing import Any


class DocsVersioning:
    """Documentation version selection and diffs."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.docs.versioning")
        self._versions: dict[str, dict[str, str]] = {}
        self._current = "latest"

    def render(self) -> dict[str, Any]:
        return {"versions": self.versions(), "current": self._current}

    def versions(self) -> list[str]:
        return list(self._versions)

    def set_version(self, version: str) -> bool:
        if version not in self._versions and version != "latest":
            return False
        self._current = version
        return True

    def diff(self, first: str, second: str) -> dict[str, Any]:
        a = self._versions.get(first, {}).get("content", "")
        b = self._versions.get(second, {}).get("content", "")
        return {"changed_lines": sum(1 for la, lb in zip(a.splitlines(), b.splitlines()) if la != lb)}
