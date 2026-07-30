from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile


class DatabaseGenerator:
    """Generates database schemas and access code."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.generation.database")

    def generate(self, schema: dict[str, Any]) -> list[CodeFile]:
        self._log.info("Generating database code")
        return []
