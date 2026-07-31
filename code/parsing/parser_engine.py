from __future__ import annotations

import logging
from typing import Any

from .ast_manager import ASTManager


class ParserEngine:
    """Central parsing engine for multiple languages."""

    def __init__(self) -> None:
        self._ast = ASTManager()
        self._log = logging.getLogger("superdev.code.parsing")

    def parse(self, code: str, language: str) -> dict[str, Any]:
        """Parse *code* in *language*.

        Python sources are handled by :class:`ASTManager` (imports, classes
        and functions extracted). Other languages fall back to a stub result.
        """
        if language.lower() == "python":
            result = self._ast.parse(code)
            if result is None:
                return {"ast": None, "errors": ["syntax error"]}
            return {
                "ast": result["ast"],
                "imports": result["imports"],
                "classes": result["classes"],
                "functions": result["functions"],
                "errors": [],
            }
        return {"ast": None, "errors": [f"No parser for {language}"]}
