"""Root cause analysis."""
from __future__ import annotations

from typing import Any


class RootCauseAnalyzer:
    def __init__(self) -> None:
        self._symptoms: dict[str, list[str]] = {}
        self._causes: dict[str, list[str]] = {}
    def add_symptom_cause(self, symptom: str, possible_causes: list[str]) -> None:
        self._symptoms[symptom] = possible_causes
        for cause in possible_causes:
            self._causes.setdefault(cause, []).append(symptom)
    def analyze(self, symptoms: list[str]) -> dict[str, Any]:
        cause_scores: dict[str, int] = {}
        for symptom in symptoms:
            for cause in self._symptoms.get(symptom, []):
                cause_scores[cause] = cause_scores.get(cause, 0) + 1
        sorted_causes = sorted(cause_scores.items(), key=lambda x: x[1], reverse=True)
        return {"symptoms": symptoms, "possible_causes": [{"cause": c, "score": s} for c, s in sorted_causes]}
    def get_causes_for_symptom(self, symptom: str) -> list[str]:
        return self._symptoms.get(symptom, [])
    def get_symptoms_for_cause(self, cause: str) -> list[str]:
        return self._causes.get(cause, [])
    def list_symptoms(self) -> list[str]:
        return list(self._symptoms.keys())
    def list_causes(self) -> list[str]:
        return list(self._causes.keys())
