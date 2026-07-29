"""Base types for the SuperDev security analysis system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityFinding:
    rule_id: str
    title: str
    description: str
    severity: Severity
    file_path: str = ""
    line: int = 0
    cve: str = ""
    cvss: float = 0.0
    recommendation: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line": self.line,
            "cve": self.cve,
            "cvss": self.cvss,
            "recommendation": self.recommendation,
        }


@dataclass
class SecurityReport:
    analyzer: str
    target: str = ""
    total_findings: int = 0
    findings: list[SecurityFinding] = field(default_factory=list)
    scan_duration_ms: float = 0.0
    error: str = ""
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def by_severity(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for f in self.findings:
            counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "analyzer": self.analyzer,
            "target": self.target,
            "total_findings": self.total_findings,
            "by_severity": self.by_severity,
            "findings": [f.to_dict() for f in self.findings],
            "scan_duration_ms": self.scan_duration_ms,
            "error": self.error,
            "timestamp": self.timestamp or datetime.now(timezone.utc).isoformat(),
            "metadata": self.metadata,
        }


class BaseCheck:
    name: str = "base"
    description: str = ""

    async def analyze(self, target: str) -> SecurityReport:
        raise NotImplementedError
