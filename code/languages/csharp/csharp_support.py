from __future__ import annotations

import logging


class CSharpSupport:
    """C# language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.csharp")

    @property
    def extensions(self) -> list[str]:
        return [".cs", ".csx"]

    def is_csharp_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
