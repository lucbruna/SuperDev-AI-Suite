from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile


class CodeGenerator:
    """Generates code from specifications."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.generation")

    def generate(self, spec: dict[str, Any]) -> list[CodeFile]:
        self._log.info("Generating code from spec: %s", spec.get("name", "unnamed"))
        return []
