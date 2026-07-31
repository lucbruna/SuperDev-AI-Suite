from __future__ import annotations

import logging


class JavaSupport:
    """Java language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.java")

    @property
    def extensions(self) -> list[str]:
        return [".java", ".class"]

    def is_java_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
