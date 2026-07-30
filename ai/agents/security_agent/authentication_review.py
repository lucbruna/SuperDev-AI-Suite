from __future__ import annotations

from typing import Any


AUTH_CHECKS: list[tuple[str, str, str]] = [
    ("password_min_length", "high", "Password minimum length not set or < 8 characters"),
    ("mfa_disabled", "high", "Multi-factor authentication not configured"),
    ("session_timeout", "medium", "Session timeout not configured or too long"),
    ("rate_limiting", "medium", "No rate limiting on login endpoint"),
    ("password_history", "low", "Password reuse prevention not configured"),
    ("account_lockout", "high", "Account lockout after failed attempts not configured"),
]


class AuthenticationReview:
    """Reviews authentication configuration for security issues."""

    def __init__(self) -> None:
        self._findings: dict[str, dict[str, Any]] = {}

    def review_config(self, config: dict[str, Any]) -> list[dict[str, Any]]:
        results = []
        for finding_id, severity, detail in AUTH_CHECKS:
            finding = {
                "id": finding_id,
                "severity": severity,
                "detail": detail,
                "passed": config.get(finding_id, False),
            }
            self._findings[finding_id] = finding
            results.append(finding)
        return results

    def add_finding(self, name: str, severity: str, detail: str) -> str:
        self._findings[name] = {"id": name, "severity": severity, "detail": detail}
        return name

    def get_finding(self, name: str) -> dict[str, Any] | None:
        return self._findings.get(name)

    def list_findings(self) -> list[dict[str, Any]]:
        return list(self._findings.values())

    @property
    def finding_count(self) -> int:
        return len(self._findings)

    def grade(self) -> str:
        if not self._findings:
            return "A"
        high_or_critical = sum(
            1 for f in self._findings.values()
            if f.get("severity", "").lower() in ("high", "critical")
        )
        if high_or_critical > 3:
            return "F"
        if high_or_critical > 1:
            return "D"
        if high_or_critical > 0:
            return "C"
        return "B"

    def to_dict(self) -> dict[str, Any]:
        return {
            "findings": list(self._findings.values()),
            "finding_count": self.finding_count,
            "grade": self.grade(),
        }
