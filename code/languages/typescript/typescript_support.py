from __future__ import annotations

import logging


class TypeScriptSupport:
    """TypeScript language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.typescript")

    @property
    def extensions(self) -> list[str]:
        return [".ts", ".tsx"]

    def is_ts_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
