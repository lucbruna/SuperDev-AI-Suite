from __future__ import annotations

from typing import Any


class ReviewConfig:
    DEFAULT_RULES = [
        {"name": "Print Statement", "pattern": r"\bprint\(", "severity": 1, "message": "Print statement in production code", "suggestion": "Use a logger instead of print()"},
        {"name": "Debug Breakpoint", "pattern": r"\bbreakpoint\(\)", "severity": 3, "message": "Debug breakpoint left in code", "suggestion": "Remove breakpoint() before committing"},
        {"name": "TODO Comment", "pattern": r"#\s*TODO", "severity": 1, "message": "TODO comment found — incomplete implementation", "suggestion": "Address the TODO before merging"},
        {"name": "FIXME Comment", "pattern": r"#\s*FIXME", "severity": 2, "message": "FIXME comment — known issue", "suggestion": "Fix the issue or create a tracking ticket"},
        {"name": "HARDCODED Config", "pattern": r"(\"https?://localhost|\"http://0\.0\.0\.0)", "severity": 3, "message": "Hardcoded localhost or 0.0.0.0 URL", "suggestion": "Use environment variable for the URL"},
        {"name": "Import *", "pattern": r"from\s+\S+\s+import\s+\*", "severity": 2, "message": "Wildcard import", "suggestion": "Import only what you need: from module import Thing"},
        {"name": "Too Many Returns", "pattern": r"^\s+return\s", "severity": 1, "message": "Multiple return statements", "suggestion": "Consider consolidating early returns"},
        {"name": "Naked Except", "pattern": r"except\s*:", "severity": 4, "message": "Bare except clause", "suggestion": "Catch specific exceptions: except ValueError:"},
        {"name": "Console.log", "pattern": r"console\.log\(", "severity": 1, "message": "console.log in frontend code", "suggestion": "Remove console.log or use a proper logging framework"},
        {"name": "TypeScript Any", "pattern": r":\s*any\b", "severity": 2, "message": "Using `any` type", "suggestion": "Use a specific type instead of `any`"},
        {"name": "Large File", "pattern": None, "severity": 2, "message": "File exceeds 400 lines", "suggestion": "Split into smaller modules"},
    ]

    def __init__(self, rules: list[dict[str, Any]] | None = None):
        self._rules = rules or self.DEFAULT_RULES
        self._severity_map = {"info": 1, "warning": 2, "error": 3, "critical": 4}

    def get_rules_for_file(self, filename: str) -> list[dict[str, Any]]:
        if filename.endswith((".py", ".pyw")):
            return [r for r in self._rules if r.get("pattern")]
        if filename.endswith((".ts", ".tsx", ".js", ".jsx")):
            return [r for r in self._rules if r.get("pattern") and r["name"] not in ("Naked Except", "Import *")]
        return [r for r in self._rules if r.get("pattern") and r.get("severity", 1) >= 3]

    def get_all_rules(self) -> list[dict[str, Any]]:
        return self._rules

    def add_rule(self, rule: dict[str, Any]) -> None:
        self._rules.append(rule)

    def remove_rule(self, name: str) -> bool:
        for i, r in enumerate(self._rules):
            if r["name"] == name:
                self._rules.pop(i)
                return True
        return False

    def set_severity(self, name: str, level: str | int) -> bool:
        if isinstance(level, str):
            level = self._severity_map.get(level, 2)
        for r in self._rules:
            if r["name"] == name:
                r["severity"] = level
                return True
        return False

    def to_dict(self) -> list[dict[str, Any]]:
        return self._rules

    @classmethod
    def from_dict(cls, rules: list[dict[str, Any]]) -> ReviewConfig:
        return cls(rules=rules)