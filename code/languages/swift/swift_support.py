from __future__ import annotations

import logging


class SwiftSupport:
    """Swift language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.swift")

    @property
    def extensions(self) -> list[str]:
        return [".swift"]

    def is_swift_file(self, path: str) -> bool:
        return path.endswith(".swift")
