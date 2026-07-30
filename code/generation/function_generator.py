from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile


class FunctionGenerator:
    """Generates function definitions from specifications."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.generation.function")

    def generate(self, name: str, params: list[dict[str, Any]]) -> CodeFile | None:
        self._log.info("Generating function: %s", name)
        return None
