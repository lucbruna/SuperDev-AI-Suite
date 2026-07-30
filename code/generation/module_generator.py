from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile, CodeLanguage


class ModuleGenerator:
    """Generates code modules from definitions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.generation.module")

    def generate(self, name: str, language: CodeLanguage) -> CodeFile | None:
        self._log.info("Generating module: %s", name)
        return None
