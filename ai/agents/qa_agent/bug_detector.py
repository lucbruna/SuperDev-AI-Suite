from __future__ import annotations

from typing import Any

BUG_PATTERNS: list[tuple[str, str, str]] = [
    ("none_check", "Variable compared to None with ==", "medium"),
    ("empty_except", "Bare except clause", "high"),
    ("mutable_default", "Mutable default argument", "medium"),
    ("infinite_loop", "Potential infinite loop (while True without break)", "high"),
    ("unused_var", "Variable assigned but never used", "low"),
    ("shadowing", "Variable shadows built-in name", "low"),
]


class BugDetector:
    """Detects common bug patterns in code."""

    def __init__(self) -> None:
        self._patterns: dict[str, dict[str, Any]] = {}
        for name, desc, severity in BUG_PATTERNS:
            self._patterns[name] = {"name": name, "description": desc, "severity": severity}

    def detect_bugs(self, code_snippet: str) -> list[dict[str, Any]]:
        results = []
        code_lower = code_snippet.lower()
        if "== none" in code_lower or "!= none" in code_lower:
            results.append({"pattern": "none_check", "severity": "medium", "description": "Use 'is None' instead of '== None'"})
        if "except:" in code_snippet and "except Exception" not in code_snippet:
            results.append({"pattern": "empty_except", "severity": "high", "description": "Bare except catches all exceptions"})
        if "def " in code_lower and "=[]" in code_snippet or "={}" in code_snippet:
            results.append({"pattern": "mutable_default", "severity": "medium", "description": "Mutable default argument"})
        return results

    def add_bug_pattern(self, name: str, pattern: str, severity: str = "medium") -> str:
        self._patterns[name] = {"name": name, "description": pattern, "severity": severity}
        return name

    def get_bug_pattern(self, name: str) -> dict[str, Any] | None:
        return self._patterns.get(name)

    def list_bug_patterns(self) -> list[dict[str, Any]]:
        return list(self._patterns.values())

    @property
    def pattern_count(self) -> int:
        return len(self._patterns)

    @property
    def critical_bugs(self) -> int:
        return sum(1 for p in self._patterns.values() if p["severity"] == "critical")

    def to_dict(self) -> dict[str, Any]:
        return {
            "patterns": list(self._patterns.values()),
            "pattern_count": self.pattern_count,
        }
