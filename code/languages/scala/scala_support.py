from __future__ import annotations

import logging


class ScalaSupport:
    """Scala language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.scala")

    @property
    def extensions(self) -> list[str]:
        return [".scala", ".sc"]

    def is_scala_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
