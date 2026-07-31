from __future__ import annotations

from typing import Any

from .consistency_checker import ConsistencyChecker
from .contradiction_detector import ContradictionDetector
from .fact_checker import FactChecker
from .hallucination_detector import HallucinationDetector
from .validation_engine import ValidationEngine


class Verifier:
    """Main verification coordinator."""

    def __init__(
        self,
        consistency: ConsistencyChecker | None = None,
        contradiction: ContradictionDetector | None = None,
        hallucination: HallucinationDetector | None = None,
        fact_checker: FactChecker | None = None,
        validation: ValidationEngine | None = None,
    ):
        self._consistency = consistency or ConsistencyChecker()
        self._contradiction = contradiction or ContradictionDetector()
        self._hallucination = hallucination or HallucinationDetector()
        self._fact_checker = fact_checker or FactChecker()
        self._validation = validation or ValidationEngine()

    async def verify(self, response: str, context: dict[str, Any]) -> dict[str, Any]:
        consistency = await self._consistency.check(response, context)
        contradiction = await self._contradiction.detect(response, context)
        hallucination = await self._hallucination.detect(response, context)
        facts = await self._fact_checker.check(response, context)
        validation = await self._validation.validate(response, context)
        passed = all(
            [
                consistency.get("consistent", False),
                not contradiction.get("has_contradiction", True),
                not hallucination.get("has_hallucination", True),
                facts.get("verified", False),
                validation.get("valid", False),
            ]
        )
        return {
            "passed": passed,
            "checks": {
                "consistency": consistency,
                "contradiction": contradiction,
                "hallucination": hallucination,
                "facts": facts,
                "validation": validation,
            },
        }
