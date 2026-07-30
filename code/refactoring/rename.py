from __future__ import annotations

import logging
from ..code_models import CodeFile


class RenameRefactoring:
    """Renames symbols across the codebase."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.refactoring.rename")

    def rename(self, files: list[CodeFile], old_name: str, new_name: str) -> list[CodeFile]:
        result: list[CodeFile] = []
        for f in files:
            content = f.content.replace(old_name, new_name)
            result.append(CodeFile(path=f.path, language=f.language, content=content, size=len(content)))
        self._log.info("Renamed %s -> %s in %d files", old_name, new_name, len(files))
        return result
