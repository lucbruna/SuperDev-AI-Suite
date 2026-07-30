from __future__ import annotations

from typing import Any


class FactChecker:
    """Verifies factual claims against a knowledge base."""

    def __init__(self) -> None:
        self._knowledge_base: dict[str, str] = {}

    def add_fact(self, claim: str, truth: str) -> None:
        self._knowledge_base[claim.lower()] = truth

    async def check(self, response: str, context: dict[str, Any]) -> dict[str, Any]:
        errors: list[dict[str, str]] = []
        for claim, truth in self._knowledge_base.items():
            if claim in response.lower():
                if truth not in response.lower():
                    errors.append({"claim": claim, "expected": truth})
        return {
            "verified": len(errors) == 0,
            "errors": errors,
            "total_claims_checked": len(self._knowledge_base),
        }
