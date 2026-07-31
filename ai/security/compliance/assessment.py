"""Compliance assessment."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid

class Assessment:
    def __init__(self, standard: str, assessor: str, scope: str = "") -> None:
        self.assessment_id = str(uuid.uuid4())[:8]
        self.standard = standard
        self.assessor = assessor
        self.scope = scope
        self.started_at = time.time()
        self.completed_at: Optional[float] = None
        self.results: List[Dict[str, Any]] = []
        self.status = "in_progress"

class ComplianceAssessor:
    def __init__(self) -> None:
        self._assessments: Dict[str, Assessment] = {}
    def start_assessment(self, standard: str, assessor: str, scope: str = "") -> Assessment:
        assessment = Assessment(standard, assessor, scope)
        self._assessments[assessment.assessment_id] = assessment
        return assessment
    def add_result(self, assessment_id: str, control: str, status: str, evidence: str = "") -> bool:
        assessment = self._assessments.get(assessment_id)
        if assessment:
            assessment.results.append({"control": control, "status": status, "evidence": evidence, "timestamp": time.time()})
            return True
        return False
    def complete(self, assessment_id: str) -> bool:
        assessment = self._assessments.get(assessment_id)
        if assessment:
            assessment.completed_at = time.time()
            assessment.status = "completed"
            return True
        return False
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        assessment = self._assessments.get(assessment_id)
        if assessment:
            passed = sum(1 for r in assessment.results if r["status"] == "pass")
            total = len(assessment.results)
            return {"id": assessment.assessment_id, "standard": assessment.standard, "status": assessment.status, "results_count": total, "passed": passed, "score": (passed / max(total, 1)) * 100}
        return None
    def list_assessments(self, standard: str = "") -> List[str]:
        if standard:
            return [a.assessment_id for a in self._assessments.values() if a.standard == standard]
        return list(self._assessments.keys())
