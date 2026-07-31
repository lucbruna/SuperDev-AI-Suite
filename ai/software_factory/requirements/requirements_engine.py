"""Core engine for requirements analysis and processing."""
from datetime import datetime
from typing import Any

from .models import RequirementSet
from .requirements_analyzer import RequirementsAnalyzer
from .requirements_parser import RequirementsParser
from .requirements_validator import RequirementsValidator


class RequirementsEngine:
    """Central engine coordinating requirements processing."""

    def __init__(self):
        self.parser = RequirementsParser()
        self.validator = RequirementsValidator()
        self.analyzer = RequirementsAnalyzer()
        self._requirement_sets: dict[str, RequirementSet] = {}
        self._processing_history: list[dict[str, Any]] = []

    def process_requirements(self, raw_data: list[dict[str, Any]]) -> RequirementSet:
        """Parse, validate, and analyze raw requirements data."""
        parsed = self.parser.parse_many(raw_data)
        validated = []
        for req in parsed:
            result = self.validator.validate(req)
            if result.is_valid:
                validated.append(req)
            self._record_processing(req.requirement_id, "validated", result.is_valid)
        req_set = RequirementSet(
            name=f"Processed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            requirements=validated,
        )
        self._requirement_sets[req_set.set_id] = req_set
        return req_set

    def get_set(self, set_id: str) -> RequirementSet | None:
        return self._requirement_sets.get(set_id)

    def analyze_set(self, set_id: str) -> dict[str, Any]:
        req_set = self._requirement_sets.get(set_id)
        if not req_set:
            return {"error": "Set not found"}
        return self.analyzer.analyze_set(req_set)

    def get_all_sets(self) -> list[RequirementSet]:
        return list(self._requirement_sets.values())

    def get_processing_history(self) -> list[dict[str, Any]]:
        return list(self._processing_history)

    def _record_processing(self, req_id: str, stage: str, success: bool) -> None:
        self._processing_history.append({
            "requirement_id": req_id,
            "stage": stage,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        })
