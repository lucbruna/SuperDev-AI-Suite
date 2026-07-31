from __future__ import annotations

import logging


class RSupport:
    """R language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.r")

    @property
    def extensions(self) -> list[str]:
        return [".r", ".R"]

    def is_r_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
