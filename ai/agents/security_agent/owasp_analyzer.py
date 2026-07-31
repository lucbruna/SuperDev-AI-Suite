from __future__ import annotations

from typing import Any

OWASP_CHECKS: list[tuple[str, str, str, str]] = [
    ("sql_injection", "SQL Injection", "critical", "Unvalidated user input in SQL queries"),
    ("xss", "Cross-Site Scripting", "critical", "Unescaped user input in HTML output"),
    ("broken_auth", "Broken Authentication", "high", "Weak session management or credentials"),
    ("sensitive_data", "Sensitive Data Exposure", "high", "Unencrypted sensitive data"),
    ("xxe", "XML External Entities", "medium", "Insecure XML parser configuration"),
    ("broken_access", "Broken Access Control", "high", "Missing authorization checks"),
    ("security_misconfig", "Security Misconfiguration", "medium", "Default or debug configs enabled"),
    ("csrf", "Cross-Site Request Forgery", "medium", "Missing CSRF tokens"),
    ("known_vulns", "Using Components with Known Vulnerabilities", "high", "Outdated libraries with CVEs"),
    ("unvalidated", "Unvalidated Redirects/Forwards", "low", "Open redirect patterns"),
]


class OWASPAnalyzer:
    """Analyzes code against OWASP Top 10 vulnerabilities."""

    def __init__(self) -> None:
        self._findings: dict[str, dict[str, Any]] = {}

    def analyze_code(self, code_snippet: str) -> list[dict[str, Any]]:
        results = []
        code_lower = code_snippet.lower()
        for finding_id, name, severity, desc in OWASP_CHECKS:
            detected = False
            if (
                finding_id == "sql_injection"
                and ("execute(" in code_snippet or "raw(" in code_lower)
                or finding_id == "xss"
                and ("innerhtml" in code_lower or "dangerouslySetInnerHTML" in code_snippet)
                or finding_id == "broken_auth"
                and "password" in code_lower
                and "hash" not in code_lower
            ):
                detected = True
            elif finding_id == "sensitive_data" and "credit" in code_lower or "ssn" in code_lower:
                detected = bool("credit" in code_lower or "ssn" in code_lower)
            if detected:
                finding = {"id": finding_id, "name": name, "severity": severity, "description": desc}
                self._findings[finding_id] = finding
                results.append(finding)
        return results

    def add_finding(self, name: str, category: str, severity: str, description: str) -> str:
        self._findings[name] = {"id": name, "name": category, "severity": severity, "description": description}
        return name

    def get_finding(self, name: str) -> dict[str, Any] | None:
        return self._findings.get(name)

    def list_findings(self, category: str | None = None) -> list[dict[str, Any]]:
        findings = list(self._findings.values())
        if category:
            findings = [f for f in findings if f.get("name", "").lower() == category.lower()]
        return findings

    @property
    def finding_count(self) -> int:
        return len(self._findings)

    @property
    def owasp_top_10(self) -> list[str]:
        return [name for _, name, _, _ in OWASP_CHECKS]

    def to_dict(self) -> dict[str, Any]:
        return {"findings": list(self._findings.values()), "finding_count": self.finding_count}
