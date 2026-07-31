from __future__ import annotations

import logging


class KotlinSupport:
    """Kotlin language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.kotlin")

    @property
    def extensions(self) -> list[str]:
        return [".kt", ".kts"]

    def is_kotlin_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
