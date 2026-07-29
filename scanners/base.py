"""Base classes and types for the SuperDev scanner system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingType(Enum):
    VULNERABILITY = "vulnerability"
    MISCONFIGURATION = "misconfiguration"
    BEST_PRACTICE = "best_practice"
    SECRET = "secret"
    DEPRECATED = "deprecated"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    DUPLICATION = "duplication"
    COMPLEXITY = "complexity"


@dataclass
class Finding:
    """A single finding from a scanner scan."""
    rule_id: str
    title: str
    description: str
    severity: Severity
    file_path: str = ""
    line: int = 0
    column: int = 0
    snippet: str = ""
    recommendation: str = ""
    type: FindingType = FindingType.VULNERABILITY
    cve: str = ""
    cvss_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanResult:
    """Result of a scanner execution."""
    scanner_name: str
    target: str = ""
    total_findings: int = 0
    findings: list[Finding] = field(default_factory=list)
    scan_duration_ms: float = 0.0
    error: str = ""
    timestamp: str = ""

    @property
    def by_severity(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for f in self.findings:
            counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
        return counts

    @property
    def has_critical(self) -> bool:
        return any(f.severity == Severity.CRITICAL for f in self.findings)

    @property
    def has_errors(self) -> bool:
        return bool(self.error)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scanner_name": self.scanner_name,
            "target": self.target,
            "total_findings": self.total_findings,
            "by_severity": self.by_severity,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "title": f.title,
                    "description": f.description,
                    "severity": f.severity.value,
                    "file_path": f.file_path,
                    "line": f.line,
                    "snippet": f.snippet,
                    "recommendation": f.recommendation,
                    "type": f.type.value,
                    "cve": f.cve,
                    "cvss_score": f.cvss_score,
                }
                for f in self.findings
            ],
            "scan_duration_ms": self.scan_duration_ms,
            "error": self.error,
            "timestamp": self.timestamp or datetime.now(timezone.utc).isoformat(),
        }


class BaseScanner:
    """Abstract base class for all scanners."""

    name: str = "base"
    description: str = ""

    async def scan(self, target: str) -> ScanResult:
        """Scan a target and return findings."""
        raise NotImplementedError

    async def scan_path(self, path: str) -> ScanResult:
        """Scan a file system path."""
        return await self.scan(path)

    async def scan_content(self, content: str, filename: str = "") -> ScanResult:
        """Scan a string content."""
        return await self.scan(f"memory:{filename}")
