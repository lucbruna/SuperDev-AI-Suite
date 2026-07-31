from __future__ import annotations

from typing import Any

DANGEROUS_PATTERNS = [
    ("eval(", "Code injection", "critical"),
    ("exec(", "Code injection", "critical"),
    ("__import__", "Dynamic import", "high"),
    ("pickle.loads", "Deserialization attack", "high"),
    ("os.system", "Shell injection", "critical"),
    ("subprocess.Popen", "Shell injection", "high"),
    ("sqlite3.execute(", "SQL injection", "critical"),
    (".format(", "Potential injection", "medium"),
    ("%s", "SQL injection risk", "high"),
]


class Security:
    """Backend security rule management and code scanning."""

    def __init__(self) -> None:
        self._rules: dict[str, dict[str, Any]] = {}

    def add_rule(self, name: str, check: str, severity: str = "medium") -> str:
        self._rules[name] = {
            "name": name,
            "check": check,
            "severity": severity.lower(),
        }
        return name

    def get_rule(self, name: str) -> dict[str, Any] | None:
        return self._rules.get(name)

    def remove_rule(self, name: str) -> bool:
        if name in self._rules:
            del self._rules[name]
            return True
        return False

    def list_rules(self, severity: str | None = None) -> list[dict[str, Any]]:
        rules = list(self._rules.values())
        if severity:
            rules = [r for r in rules if r["severity"] == severity.lower()]
        return rules

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    def scan_code(self, code_snippet: str) -> list[dict[str, Any]]:
        findings = []
        for pattern, description, severity in DANGEROUS_PATTERNS:
            if pattern in code_snippet:
                findings.append(
                    {
                        "pattern": pattern,
                        "description": description,
                        "severity": severity,
                        "line": code_snippet[: code_snippet.index(pattern)].count("\n") + 1,
                    }
                )
        return findings

    def to_dict(self) -> dict[str, Any]:
        return {
            "rules": list(self._rules.values()),
            "rule_count": self.rule_count,
        }
