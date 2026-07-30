from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile


class BackendGenerator:
    """Generates backend code from specifications."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.generation.backend")

    def generate(self, spec: dict[str, Any]) -> list[CodeFile]:
        self._log.info("Generating backend code")
        return []
