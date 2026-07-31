"""
Static Application Security Testing
"""
from dataclasses import dataclass
from enum import Enum


class RuleSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingType(Enum):
    INJECTION = "injection"
    HARDCODED_SECRET = "hardcoded_secret"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_CRYPTO = "insecure_crypto"
    XSS = "xss"
    SSRF = "ssrf"


@dataclass
class SASTRule:
    rule_id: str
    name: str
    pattern: str
    finding_type: FindingType
    severity: RuleSeverity = RuleSeverity.MEDIUM
    description: str = ""
    enabled: bool = True


@dataclass
class SASTFinding:
    rule_id: str
    file_path: str
    line_number: int
    code_snippet: str
    severity: RuleSeverity = RuleSeverity.MEDIUM
    message: str = ""


class SASTEngine:
    def __init__(self):
        self.rules: dict[str, SASTRule] = {}
        self.findings: list[SASTFinding] = []

    def add_rule(self, rule: SASTRule) -> None:
        self.rules[rule.rule_id] = rule

    def scan_code(self, file_path: str, code: str) -> list[SASTFinding]:
        findings = []
        lines = code.split("\n")
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            for i, line in enumerate(lines, 1):
                if rule.pattern.lower() in line.lower():
                    finding = SASTFinding(rule_id=rule.rule_id, file_path=file_path, line_number=i, code_snippet=line.strip(), severity=rule.severity, message=f"Detected: {rule.name}")
                    findings.append(finding)
        self.findings.extend(findings)
        return findings

    def get_findings(self, file_path: str = None, severity: RuleSeverity = None) -> list[SASTFinding]:
        results = self.findings
        if file_path:
            results = [f for f in results if f.file_path == file_path]
        if severity:
            results = [f for f in results if f.severity == severity]
        return results

    def disable_rule(self, rule_id: str) -> bool:
        rule = self.rules.get(rule_id)
        if rule:
            rule.enabled = False
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        rule = self.rules.get(rule_id)
        if rule:
            rule.enabled = True
            return True
        return False

    def clear_findings(self) -> None:
        self.findings.clear()

    def count(self) -> int:
        return len(self.rules)
