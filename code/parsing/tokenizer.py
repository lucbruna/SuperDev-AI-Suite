from __future__ import annotations

import logging
from typing import Any


class Tokenizer:
    """Tokenizes source code into tokens."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.parsing.tokenizer")

    def tokenize(self, code: str) -> list[dict[str, Any]]:
        return []
