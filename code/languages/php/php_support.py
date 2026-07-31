from __future__ import annotations

import logging


class PhpSupport:
    """PHP language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.php")

    @property
    def extensions(self) -> list[str]:
        return [".php", ".phtml"]

    def is_php_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
