from __future__ import annotations

import logging


class PythonSupport:
    """Python language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.python")

    @property
    def extensions(self) -> list[str]:
        return [".py", ".pyw", ".pyx"]

    def is_python_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
