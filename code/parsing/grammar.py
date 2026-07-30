from __future__ import annotations

import logging
from typing import Any


class Grammar:
    """Defines language grammar rules for parsing."""

    def __init__(self) -> None:
        self._rules: dict[str, Any] = {}
        self._log = logging.getLogger("superdev.code.parsing.grammar")

    def add_rule(self, name: str, pattern: Any) -> None:
        self._rules[name] = pattern

    def get_rule(self, name: str) -> Any | None:
        return self._rules.get(name)
