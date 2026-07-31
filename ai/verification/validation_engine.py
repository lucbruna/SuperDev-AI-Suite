from __future__ import annotations

from typing import Any

from .logical_validator import LogicalValidator
from .output_validator import OutputValidator
from .semantic_validator import SemanticValidator


class ValidationEngine:
    """Orchestrates multiple validation strategies."""

    def __init__(
        self,
        logical: LogicalValidator | None = None,
        semantic: SemanticValidator | None = None,
        output: OutputValidator | None = None,
    ):
        self._logical = logical or LogicalValidator()
        self._semantic = semantic or SemanticValidator()
        self._output = output or OutputValidator()

    async def validate(self, response: str, context: dict[str, Any]) -> dict[str, Any]:
        logical = await self._logical.validate(response, context)
        semantic = await self._semantic.validate(response, context)
        output = await self._output.validate(response, context)
        return {
            "valid": all([logical.get("valid", False), semantic.get("valid", False), output.get("valid", False)]),
            "logical": logical,
            "semantic": semantic,
            "output": output,
        }
