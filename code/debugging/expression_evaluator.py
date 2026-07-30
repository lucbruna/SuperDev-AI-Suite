from __future__ import annotations

import logging
from typing import Any


class ExpressionEvaluator:
    """Evaluates expressions in the debug context."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.debugging.expressions")

    def evaluate(self, expression: str, context: dict[str, Any] | None = None) -> Any | None:
        self._log.debug("Evaluating: %s", expression)
        return None

    def validate(self, expression: str) -> bool:
        return bool(expression and expression.strip())
