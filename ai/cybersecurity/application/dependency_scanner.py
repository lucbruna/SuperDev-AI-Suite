"""
Dependency Vulnerability Scanner
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    vuln_id: str
    package: str
    version: str
    fixed_version: str = ""
    severity: Severity = Severity.MEDIUM
    description: str = ""
    cve_ids: List[str] = field(default_factory=list)
    cvss_score: float = 0.0


@dataclass
class Dependency:
    name: str
    version: str
    ecosystem: str = "pypi"
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ScanResult:
    total_dependencies: int
    vulnerable_count: int
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    risk_score: float = 0.0


class DependencyScanner:
    def __init__(self):
        self.dependencies: Dict[str, Dependency] = {}
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.known_vulns: List[Vulnerability] = []

    def add_dependency(self, name: str, version: str, ecosystem: str = "pypi") -> Dependency:
        dep = Dependency(name=name, version=version, ecosystem=ecosystem)
        self.dependencies[name] = dep
        return dep

    def add_vulnerability(self, vuln: Vulnerability) -> None:
        self.known_vulns.append(vuln)
        self.vulnerabilities[vuln.vuln_id] = vuln

    def scan(self) -> ScanResult:
        found = []
        for dep in self.dependencies.values():
            for vuln in self.known_vulns:
                if vuln.package == dep.name and vuln.version == dep.version:
                    found.append(vuln)
        risk = sum(v.cvss_score for v in found) / max(len(found), 1)
        return ScanResult(total_dependencies=len(self.dependencies), vulnerable_count=len(found), vulnerabilities=found, risk_score=risk)

    def get_vulnerable(self) -> List[Vulnerability]:
        found = []
        for dep in self.dependencies.values():
            for vuln in self.known_vulns:
                if vuln.package == dep.name and vuln.version == dep.version:
                    found.append(vuln)
        return found

    def update_dependency(self, name: str, version: str) -> bool:
        if name in self.dependencies:
            self.dependencies[name].version = version
            return True
        return False

    def get_dependency(self, name: str) -> Optional[Dependency]:
        return self.dependencies.get(name)

    def count(self) -> int:
        return len(self.dependencies)
