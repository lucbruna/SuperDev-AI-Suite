from __future__ import annotations

from typing import Any

A11Y_CHECKS: list[tuple[str, str, str]] = [
    ("aria-label", "Element missing aria-label", "A"),
    ("role=", "Element missing role attribute", "A"),
    ("onKey", "Missing keyboard handler", "AA"),
    ("tabIndex", "Missing tab order", "A"),
    ("alt=", "Image missing alt text", "A"),
    ("aria-hidden", "Missing aria-hidden on decorative elements", "A"),
    ("aria-expanded", "Missing aria-expanded on toggle", "AA"),
    ("aria-live", "Missing aria-live on dynamic content", "AA"),
]


class Accessibility:
    """Analyzes frontend code for accessibility issues."""

    def __init__(self) -> None:
        self._rules: dict[str, dict[str, Any]] = {}
        for name, check, level in A11Y_CHECKS:
            self._rules[name] = {"name": name, "check": check, "wcag_level": level}

    def analyze_component(self, component_code: str) -> list[dict[str, Any]]:
        issues = []
        for name, check, level in A11Y_CHECKS:
            if check not in component_code and name not in component_code:
                issues.append({
                    "rule": name,
                    "description": check,
                    "wcag_level": level,
                    "present": False,
                })
        return issues

    def add_rule(self, name: str, check: str, wcag_level: str = "A") -> str:
        self._rules[name] = {"name": name, "check": check, "wcag_level": wcag_level}
        return name

    def get_rule(self, name: str) -> dict[str, Any] | None:
        return self._rules.get(name)

    def list_rules(self, level: str | None = None) -> list[dict[str, Any]]:
        rules = list(self._rules.values())
        if level:
            rules = [r for r in rules if r["wcag_level"] == level.upper()]
        return rules

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    def generate_a11y_fixes(self, issues: list[dict[str, Any]]) -> list[str]:
        fixes = []
        for issue in issues:
            name = issue.get("rule", "")
            fixes.append(f"Add {name} attribute to element")
        return fixes if fixes else ["No issues found"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "rules": list(self._rules.values()),
            "rule_count": self.rule_count,
        }
