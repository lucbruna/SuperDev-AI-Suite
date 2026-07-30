from __future__ import annotations

from typing import Any

from .audit import Audit
from .authentication_review import AuthenticationReview
from .authorization_review import AuthorizationReview
from .dependency_scanner import DependencyScanner
from .encryption_review import EncryptionReview
from .owasp_analyzer import OWASPAnalyzer
from .permissions_analyzer import PermissionsAnalyzer
from .secrets_detector import SecretsDetector
from .vulnerability_report import VulnerabilityReport


class SecurityAgent:
    """Central orchestrator for security analysis and audit."""

    def __init__(self) -> None:
        self._owasp = OWASPAnalyzer()
        self._dep_scanner = DependencyScanner()
        self._secrets = SecretsDetector()
        self._permissions = PermissionsAnalyzer()
        self._vuln_report = VulnerabilityReport()
        self._auth_review = AuthenticationReview()
        self._authz_review = AuthorizationReview()
        self._encryption = EncryptionReview()
        self._audit = Audit()

    @property
    def owasp(self) -> OWASPAnalyzer:
        return self._owasp

    @property
    def dependency_scanner(self) -> DependencyScanner:
        return self._dep_scanner

    @property
    def secrets_detector(self) -> SecretsDetector:
        return self._secrets

    @property
    def permissions(self) -> PermissionsAnalyzer:
        return self._permissions

    @property
    def vulnerability_report(self) -> VulnerabilityReport:
        return self._vuln_report

    @property
    def auth_review(self) -> AuthenticationReview:
        return self._auth_review

    @property
    def authz_review(self) -> AuthorizationReview:
        return self._authz_review

    @property
    def encryption(self) -> EncryptionReview:
        return self._encryption

    @property
    def audit(self) -> Audit:
        return self._audit

    def run_security_audit(self, target: dict[str, Any]) -> dict[str, Any]:
        code = target.get("code", "")
        findings = self._owasp.analyze_code(code)
        secrets = self._secrets.scan_text(code)
        return {
            "status": "completed",
            "owasp_findings": len(findings),
            "secrets_found": len(secrets),
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "owasp_findings": self._owasp.finding_count,
            "dependencies": self._dep_scanner.dependency_count,
            "vulnerabilities": self._vuln_report.total_count,
            "audit_events": self._audit.event_count,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"agent": "security_agent", "status": self.get_status()}
