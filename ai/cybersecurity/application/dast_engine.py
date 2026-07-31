"""
Dynamic Application Security Testing
"""

import secrets
from dataclasses import dataclass, field
from enum import Enum


class VulnSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DASTVulnerability:
    vuln_id: str
    url: str
    vulnerability_type: str
    severity: VulnSeverity = VulnSeverity.MEDIUM
    evidence: str = ""
    remediation: str = ""
    request: str = ""
    response: str = ""


@dataclass
class ScanTarget:
    url: str
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    parameters: dict[str, str] = field(default_factory=dict)


@dataclass
class DASTReport:
    target_url: str
    total_requests: int
    vulnerabilities_found: int
    vulnerabilities: list[DASTVulnerability] = field(default_factory=list)
    risk_score: float = 0.0


class DASTEngine:
    def __init__(self):
        self.vulnerabilities: list[DASTVulnerability] = []
        self.targets: list[ScanTarget] = []
        self.fuzz_payloads: list[str] = [
            "' OR '1'='1",
            "<script>alert(1)</script>",
            "../../etc/passwd",
            "{{7*7}}",
            "${7*7}",
            ";ls -la",
            "UNION SELECT * FROM users",
        ]

    def add_target(self, url: str, method: str = "GET", headers: dict[str, str] = None) -> ScanTarget:
        target = ScanTarget(url=url, method=method, headers=headers or {})
        self.targets.append(target)
        return target

    def scan_target(self, target: ScanTarget) -> list[DASTVulnerability]:
        findings = []
        for payload in self.fuzz_payloads:
            if any(k in payload.lower() for k in ["select", "union", "or '", "script"]):
                vuln = DASTVulnerability(
                    vuln_id=secrets.token_hex(8),
                    url=target.url,
                    vulnerability_type="injection",
                    severity=VulnSeverity.HIGH,
                    evidence=payload,
                )
                findings.append(vuln)
        self.vulnerabilities.extend(findings)
        return findings

    def run_full_scan(self) -> DASTReport:
        all_findings = []
        for target in self.targets:
            all_findings.extend(self.scan_target(target))
        risk = sum(
            1 if v.severity == VulnSeverity.CRITICAL else 2 if v.severity == VulnSeverity.HIGH else 3
            for v in all_findings
        ) / max(len(all_findings), 1)
        return DASTReport(
            target_url=self.targets[0].url if self.targets else "",
            total_requests=len(self.targets) * len(self.fuzz_payloads),
            vulnerabilities_found=len(all_findings),
            vulnerabilities=all_findings,
            risk_score=risk,
        )

    def get_vulnerabilities(self, severity: VulnSeverity = None) -> list[DASTVulnerability]:
        if severity:
            return [v for v in self.vulnerabilities if v.severity == severity]
        return self.vulnerabilities

    def add_fuzz_payload(self, payload: str) -> None:
        self.fuzz_payloads.append(payload)

    def clear_results(self) -> None:
        self.vulnerabilities.clear()

    def count(self) -> int:
        return len(self.vulnerabilities)
