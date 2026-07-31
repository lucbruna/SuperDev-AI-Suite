"""
Security-Focused Code Quality Analysis
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class QualityRule(Enum):
    NO_EVAL = "no_eval"
    NO_EXEC = "no_exec"
    USE_PARAMETERIZED = "use_parameterized_queries"
    VALIDATE_INPUT = "validate_input"
    ENCODE_OUTPUT = "encode_output"
    USE_TLS = "use_tls"
    AVOID_HARDcoded = "avoid_hardcoded_secrets"
    LOG_SENSITIVE = "log_sensitive_data"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class QualityFinding:
    rule: QualityRule
    file_path: str
    line_number: int
    snippet: str
    severity: Severity = Severity.MEDIUM
    suggestion: str = ""


class CodeQualityAnalyzer:
    def __init__(self):
        self.findings: list[QualityFinding] = []
        self.rules_config: dict[QualityRule, dict[str, Any]] = {
            QualityRule.NO_EVAL: {"patterns": ["eval(", "exec("], "severity": Severity.CRITICAL},
            QualityRule.VALIDATE_INPUT: {"patterns": ["request.args", "request.form"], "severity": Severity.HIGH},
            QualityRule.LOG_SENSITIVE: {
                "patterns": ["print(password", "log(password", "print(token"],
                "severity": Severity.HIGH,
            },
            QualityRule.AVOID_HARDcoded: {"patterns": ['password = "', 'api_key = "'], "severity": Severity.CRITICAL},
        }

    def analyze_file(self, file_path: str, content: str) -> list[QualityFinding]:
        findings = []
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for rule, config in self.rules_config.items():
                for pattern in config["patterns"]:
                    if pattern in line:
                        finding = QualityFinding(
                            rule=rule,
                            file_path=file_path,
                            line_number=line_num,
                            snippet=line.strip()[:100],
                            severity=config["severity"],
                            suggestion=f"Avoid: {rule.value}",
                        )
                        findings.append(finding)
        self.findings.extend(findings)
        return findings

    def get_findings(self, severity: Severity = None) -> list[QualityFinding]:
        if severity:
            return [f for f in self.findings if f.severity == severity]
        return self.findings

    def add_rule(self, rule: QualityRule, patterns: list[str], severity: Severity = Severity.MEDIUM) -> None:
        self.rules_config[rule] = {"patterns": patterns, "severity": severity}

    def get_score(self) -> float:
        if not self.findings:
            return 100.0
        penalties = sum(
            10 if f.severity == Severity.CRITICAL else 5 if f.severity == Severity.HIGH else 2 for f in self.findings
        )
        return max(0, 100.0 - penalties)

    def clear(self) -> None:
        self.findings.clear()

    def count(self) -> int:
        return len(self.findings)
