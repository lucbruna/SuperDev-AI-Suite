from __future__ import annotations

import logging


class GoSupport:
    """Go language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.go")

    @property
    def extensions(self) -> list[str]:
        return [".go"]

    def is_go_file(self, path: str) -> bool:
        return path.endswith(".go")
