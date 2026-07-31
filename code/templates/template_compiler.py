from __future__ import annotations

import logging
from typing import Any


class TemplateCompiler:
    """Compiles raw template source strings into executable form."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.templates.compiler")

    def compile(self, source: str, name: str = "<template>") -> Any:
        raise NotImplementedError

    def compile_file(self, path: str) -> Any:
        with open(path, encoding="utf-8") as f:
            return self.compile(f.read(), path)
