from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile


class DocumentationGenerator:
    """Generates documentation from code."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.generation.docs")

    def generate(self, spec: dict[str, Any]) -> list[CodeFile]:
        self._log.info("Generating documentation")
        return []
