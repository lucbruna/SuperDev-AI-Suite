"""Diagnostics subsystem generator."""
import os

BASE = r'C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\observability\diagnostics'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

w('diagnostics_engine.py', '''"""Diagnostics engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional

class DiagnosticsEngine:
    def __init__(self) -> None:
        self._analyzers: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []
    def register_analyzer(self, name: str, analyzer: Any) -> None:
        self._analyzers[name] = analyzer
    def diagnose(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = {"problem": problem, "context": context or {}, "findings": [], "recommendations": []}
        for name, analyzer in self._analyzers.items():
            if hasattr(analyzer, 'analyze'):
                try:
                    finding = analyzer.analyze(problem, context or {})
                    result["findings"].append({"analyzer": name, "finding": finding})
                except Exception as e:
                    result["findings"].append({"analyzer": name, "error": str(e)})
        self._history.append(result)
        return result
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._history[-limit:]
    def list_analyzers(self) -> List[str]:
        return list(self._analyzers.keys())
''')

w('root_cause.py', '''"""Root cause analysis."""
from __future__ import annotations
from typing import Any, Dict, List

class RootCauseAnalyzer:
    def __init__(self) -> None:
        self._symptoms: Dict[str, List[str]] = {}
        self._causes: Dict[str, List[str]] = {}
    def add_symptom_cause(self, symptom: str, possible_causes: List[str]) -> None:
        self._symptoms[symptom] = possible_causes
        for cause in possible_causes:
            self._causes.setdefault(cause, []).append(symptom)
    def analyze(self, symptoms: List[str]) -> Dict[str, Any]:
        cause_scores: Dict[str, int] = {}
        for symptom in symptoms:
            for cause in self._symptoms.get(symptom, []):
                cause_scores[cause] = cause_scores.get(cause, 0) + 1
        sorted_causes = sorted(cause_scores.items(), key=lambda x: x[1], reverse=True)
        return {"symptoms": symptoms, "possible_causes": [{"cause": c, "score": s} for c, s in sorted_causes]}
    def get_causes_for_symptom(self, symptom: str) -> List[str]:
        return self._symptoms.get(symptom, [])
    def get_symptoms_for_cause(self, cause: str) -> List[str]:
        return self._causes.get(cause, [])
    def list_symptoms(self) -> List[str]:
        return list(self._symptoms.keys())
    def list_causes(self) -> List[str]:
        return list(self._causes.keys())
''')

w('analyzer.py', '''"""General analyzer."""
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
''')

w('recommendation.py', '''"""Recommendation engine."""
from __future__ import annotations
from typing import Any, Dict, List

class RecommendationEngine:
    def __init__(self) -> None:
        self._templates: Dict[str, List[str]] = {}
    def add_template(self, category: str, recommendations: List[str]) -> None:
        self._templates[category] = recommendations
    def get_recommendations(self, category: str, context: Dict[str, Any]) -> List[str]:
        base = self._templates.get(category, [])
        context_recs = []
        if "error_type" in context:
            context_recs.append(f"Address {context['error_type']} error specifically")
        if "component" in context:
            context_recs.append(f"Focus on {context['component']} component")
        return base + context_recs
    def list_categories(self) -> List[str]:
        return list(self._templates.keys())
    def remove_template(self, category: str) -> bool:
        if category in self._templates:
            del self._templates[category]
            return True
        return False
''')

w('auto_fix.py', '''"""Auto-fix capability."""
from __future__ import annotations
from typing import Any, Callable, Dict, List

class AutoFix:
    def __init__(self) -> None:
        self._fixes: Dict[str, Callable[[], bool]] = {}
        self._history: List[Dict[str, Any]] = []
    def register_fix(self, issue_type: str, fix_func: Callable[[], bool]) -> None:
        self._fixes[issue_type] = fix_func
    def attempt_fix(self, issue_type: str) -> Dict[str, Any]:
        fix = self._fixes.get(issue_type)
        if not fix:
            return {"issue": issue_type, "status": "no_fix_available"}
        try:
            success = fix()
            result = {"issue": issue_type, "status": "fixed" if success else "fix_failed"}
        except Exception as e:
            result = {"issue": issue_type, "status": "error", "error": str(e)}
        self._history.append(result)
        return result
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._history[-limit:]
    def list_fixes(self) -> List[str]:
        return list(self._fixes.keys())
    def remove_fix(self, issue_type: str) -> bool:
        if issue_type in self._fixes:
            del self._fixes[issue_type]
            return True
        return False
''')

w('history.py', '''"""Diagnostics history."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class DiagnosticsHistory:
    def __init__(self, max_entries: int = 500) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._max = max_entries
    def record(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        entry = {"diagnosis": diagnosis, "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return entry
    def query(self, problem: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        results = self._entries
        if problem:
            results = [e for e in results if problem.lower() in str(e.get("diagnosis", {})).lower()]
        return results[-limit:]
    def count(self) -> int:
        return len(self._entries)
    def clear(self) -> int:
        n = len(self._entries)
        self._entries.clear()
        return n
    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._entries[-limit:]
''')

w('__init__.py', '''"""Diagnostics subsystem."""
from .diagnostics_engine import DiagnosticsEngine
from .root_cause import RootCauseAnalyzer
from .analyzer import GeneralAnalyzer
from .recommendation import RecommendationEngine
from .auto_fix import AutoFix
from .history import DiagnosticsHistory

__all__ = [
    "DiagnosticsEngine", "RootCauseAnalyzer", "GeneralAnalyzer",
    "RecommendationEngine", "AutoFix", "DiagnosticsHistory"
]
''')

print("diagnostics/: 7 files created")
