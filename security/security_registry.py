"""Registry of findings, certificates, secrets, threats and scans (Volume 16)."""

from __future__ import annotations

import time
from typing import Any

from .base import SecurityFinding, SecurityReport, Severity


class SecurityRegistry:
    """Central registry keeping track of all security artifacts."""

    def __init__(self) -> None:
        self._findings: list[SecurityFinding] = []
        self._reports: dict[str, SecurityReport] = {}
        self._threats: dict[str, Any] = {}
        self._certificates: dict[str, Any] = {}
        self._vault: dict[str, Any] = {}
        self._scans: dict[str, Any] = {}
        self._artifacts: dict[str, Any] = {}

    # -- artifacts (subsystem instances) -------------------------------------

    def register_artifact(self, name: str, artifact: Any) -> None:
        self._artifacts[name] = artifact

    def artifact(self, name: str) -> Any | None:
        return self._artifacts.get(name)

    def artifacts(self) -> dict[str, Any]:
        return dict(self._artifacts)

    # -- findings / reports --------------------------------------------------

    def register_finding(self, finding: SecurityFinding) -> None:
        self._findings.append(finding)

    def register_report(self, report: SecurityReport) -> None:
        self._reports[report.target] = report
        for finding in report.findings:
            self.register_finding(finding)

    def findings(self, severity: Severity | None = None) -> list[SecurityFinding]:
        if severity is None:
            return list(self._findings)
        return [f for f in self._findings if f.severity == severity]

    def reports(self) -> list[SecurityReport]:
        return list(self._reports.values())

    # -- threats / certificates / secrets ------------------------------------

    def register_threat(self, threat: Any) -> None:
        self._threats[getattr(threat, "threat_id", str(len(self._threats)))] = threat

    def register_certificate(self, cert: Any) -> None:
        self._certificates[getattr(cert, "serial", str(len(self._certificates)))] = cert

    def register_secret(self, name: str, secret: Any) -> None:
        self._vault[name] = secret

    def register_scan(self, target: str, scan: Any) -> None:
        self._scans[target] = {"scan": scan, "ts": time.time()}

    # -- summary -------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        by_severity: dict[str, int] = {}
        for finding in self._findings:
            by_severity[finding.severity.value] = by_severity.get(
                finding.severity.value, 0
            ) + 1
        return {
            "findings": len(self._findings),
            "by_severity": by_severity,
            "reports": len(self._reports),
            "threats": len(self._threats),
            "certificates": len(self._certificates),
            "vault_secrets": len(self._vault),
            "scans": len(self._scans),
        }
