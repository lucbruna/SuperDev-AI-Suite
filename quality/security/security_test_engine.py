from __future__ import annotations

import hashlib
from typing import Any

from ..quality_models import TestSeverity, VulnerabilityFinding


class SecurityTestEngine:
    """Security testing — vulnerability scan, penetration, auth, authorization, API security, dependency scan."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.security
        self._findings: dict[str, VulnerabilityFinding] = {}
        self._dependencies: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- finding helpers -----------------------------------------------------

    def _add_finding(
        self,
        title: str,
        severity: TestSeverity,
        description: str = "",
        location: str = "",
        recommendation: str = "",
    ) -> VulnerabilityFinding:
        finding = VulnerabilityFinding(
            severity=severity,
            title=title,
            description=description,
            location=location,
            recommendation=recommendation,
        )
        self._findings[finding.finding_id] = finding
        self.engine.registry.register_finding(finding)
        self.engine.metrics.increment(
            "security.findings", labels={"severity": severity.value}
        )
        return finding

    # -- vulnerability scan --------------------------------------------------

    def vulnerability_scan(self, target: str, code: str) -> list[VulnerabilityFinding]:
        """Heuristic static scan for common vulnerability patterns."""
        findings: list[VulnerabilityFinding] = []
        patterns = {
            "eval(": (TestSeverity.HIGH, "Dynamic code execution (eval) detected"),
            "exec(": (TestSeverity.HIGH, "Shell/command execution detected"),
            "pickle.loads": (TestSeverity.HIGH, "Unsafe deserialization (pickle)"),
            "password =": (TestSeverity.MEDIUM, "Hardcoded-looking password assignment"),
            "http://": (TestSeverity.LOW, "Plain HTTP endpoint detected"),
        }
        for pattern, (severity, message) in patterns.items():
            if pattern in code:
                findings.append(self._add_finding(
                    title=message,
                    severity=severity,
                    location=f"{target}:{pattern}",
                    recommendation="Review and harden the flagged pattern.",
                ))
        if not findings:
            self.engine.metrics.increment("security.scans_clean")
        return findings

    # -- dependency scan -----------------------------------------------------

    def scan_dependency(self, name: str, version: str) -> dict[str, Any]:
        """Heuristic dependency risk assessment."""
        risk = "low"
        if any(keyword in name.lower() for keyword in ("deprecated", "unmaintained")):
            risk = "high"
        elif int(version.split(".")[0]) == 0:
            risk = "medium"
        entry = {
            "name": name,
            "version": version,
            "risk": risk,
            "sha256": hashlib.sha256(f"{name}@{version}".encode()).hexdigest()[:16],
        }
        self._dependencies[name] = entry
        if risk != "low":
            self._add_finding(
                title=f"Dependency risk: {name}",
                severity=TestSeverity.MEDIUM if risk == "medium" else TestSeverity.HIGH,
                location=f"dependency:{name}",
                recommendation=f"Upgrade or replace {name}@{version}.",
            )
        return entry

    # -- authentication / authorization --------------------------------------

    def authentication_test(self, credentials: dict[str, Any]) -> dict[str, Any]:
        """Simulate an authentication attempt and report weaknesses."""
        weak = "password" in credentials and len(str(credentials["password"])) < 8
        no_mfa = not credentials.get("mfa")
        result = {
            "authenticated": bool(credentials.get("authenticated")),
            "weak_password": weak,
            "missing_mfa": no_mfa,
        }
        if weak:
            self._add_finding(
                title="Weak password policy",
                severity=TestSeverity.MEDIUM,
                location="auth:password_policy",
                recommendation="Enforce 8+ character passwords.",
            )
        if no_mfa:
            self._add_finding(
                title="MFA not enforced",
                severity=TestSeverity.MEDIUM,
                location="auth:mfa",
                recommendation="Enable multi-factor authentication.",
            )
        return result

    def authorization_test(self, roles: dict[str, Any], action: str, role: str) -> bool:
        """Check whether a role can perform an action (RBAC)."""
        allowed = roles.get(role, set())
        return action in allowed

    # -- API security --------------------------------------------------------

    def api_security_scan(self, endpoints: list[str]) -> dict[str, Any]:
        """Flag common API security gaps by path inspection."""
        findings: list[VulnerabilityFinding] = []
        sensitive = {"admin", "internal", "debug", "password", "token", "secret"}
        for endpoint in endpoints:
            parts = [p for p in endpoint.lower().split("/") if p]
            if any(part in sensitive for part in parts):
                findings.append(self._add_finding(
                    title=f"Sensitive endpoint exposed: {endpoint}",
                    severity=TestSeverity.HIGH,
                    location=f"api:{endpoint}",
                    recommendation="Protect the endpoint with authentication and rate limits.",
                ))
        return {
            "endpoints": len(endpoints),
            "sensitive_exposed": len(findings),
            "findings": findings,
        }

    # -- summary -------------------------------------------------------------

    def list_findings(self) -> list[VulnerabilityFinding]:
        return list(self._findings.values())

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "findings": len(self._findings),
            "dependencies": len(self._dependencies),
        }


__all__ = ["SecurityTestEngine"]
