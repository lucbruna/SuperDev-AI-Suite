"""General analyzer."""
from __future__ import annotations
from typing import Any, Dict, List

class GeneralAnalyzer:
    def __init__(self) -> None:
        self._rules: List[Dict[str, Any]] = []
    def add_rule(self, pattern: str, diagnosis: str, recommendation: str) -> None:
        self._rules.append({"pattern": pattern, "diagnosis": diagnosis, "recommendation": recommendation})
    def analyze(self, problem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        matches = []
        for rule in self._rules:
            if rule["pattern"].lower() in problem.lower():
                matches.append({"diagnosis": rule["diagnosis"], "recommendation": rule["recommendation"]})
        return {"problem": problem, "matches": matches, "confidence": min(len(matches) * 0.3, 1.0)}
    def list_rules(self) -> List[Dict[str, Any]]:
        return list(self._rules)
    def remove_rule(self, index: int) -> bool:
        if 0 <= index < len(self._rules):
            self._rules.pop(index)
            return True
        return False
