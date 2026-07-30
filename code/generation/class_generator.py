from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile


class ClassGenerator:
    """Generates class definitions from specifications."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.generation.class")

    def generate(self, name: str, fields: list[dict[str, Any]]) -> CodeFile | None:
        self._log.info("Generating class: %s", name)
        return None
