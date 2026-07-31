from __future__ import annotations

import logging


class CppSupport:
    """C++ language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.cpp")

    @property
    def extensions(self) -> list[str]:
        return [".cpp", ".hpp", ".cc", ".h", ".cxx"]

    def is_cpp_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
