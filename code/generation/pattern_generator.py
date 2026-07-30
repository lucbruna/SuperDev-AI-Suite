from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile


class PatternGenerator:
    """Generates code from design patterns."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.generation.pattern")

    def generate(self, pattern: str, spec: dict[str, Any]) -> list[CodeFile]:
        self._log.info("Generating pattern: %s", pattern)
        return []
