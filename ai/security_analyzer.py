from __future__ import annotations

import json
import logging
import re
import subprocess  # nosec
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("superdev.ai.security")


class VulnerabilitySeverity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OwaspCategory(str, Enum):
    BROKEN_ACCESS_CONTROL = "A01_broken_access_control"
    CRYPTOGRAPHIC_FAILURES = "A02_cryptographic_failures"
    INJECTION = "A03_injection"
    INSECURE_DESIGN = "A04_insecure_design"
    SECURITY_MISCONFIGURATION = "A05_security_misconfiguration"
    VULNERABLE_COMPONENTS = "A06_vulnerable_components"
    AUTH_FAILURES = "A07_auth_failures"
    DATA_INTEGRITY_FAILURES = "A08_data_integrity_failures"
    LOGGING_MONITORING_FAILURES = "A09_logging_monitoring_failures"
    SSRF = "A10_ssrf"


@dataclass
class RemediationSuggestion:
    description: str
    effort: str = "medium"
    priority: str = "medium"
    code_example: Optional[str] = None
    references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "effort": self.effort,
            "priority": self.priority,
            "code_example": self.code_example[:500] if self.code_example else None,
            "references": self.references,
        }


@dataclass
class SecurityVulnerability:
    vuln_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    title: str = ""
    description: str = ""
    severity: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    cvss_score: float = 0.0
    owasp_category: Optional[OwaspCategory] = None
    cve_id: Optional[str] = None
    line_number: int = 0
    snippet: str = ""
    remediation: Optional[RemediationSuggestion] = None
    source: str = "pattern"
    file_path: Optional[str] = None
    package_name: Optional[str] = None
    installed_version: Optional[str] = None
    fixed_version: Optional[str] = None
    confidence: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        return {
            "vuln_id": self.vuln_id,
            "title": self.title,
            "description": self.description[:500],
            "severity": self.severity.value,
            "cvss_score": self.cvss_score,
            "owasp_category": self.owasp_category.value if self.owasp_category else None,
            "cve_id": self.cve_id,
            "line_number": self.line_number,
            "snippet": self.snippet[:300],
            "remediation": self.remediation.to_dict() if self.remediation else None,
            "source": self.source,
            "package_name": self.package_name,
            "installed_version": self.installed_version,
            "fixed_version": self.fixed_version,
            "confidence": self.confidence,
        }


OWASP_PATTERNS: list[dict[str, Any]] = [
    {
        "category": OwaspCategory.INJECTION,
        "patterns": [
            (r"execute\s*\(\s*f['\"]", 0.9, "SQL injection via f-string in execute()"),
            (r"eval\s*\(", 0.95, "Use of eval() allows arbitrary code execution"),
            (r"exec\s*\(", 0.95, "Use of exec() allows arbitrary code execution"),
            (r"subprocess\.call\s*\(.*shell\s*=\s*True", 0.85, "Shell=True enables command injection"),
            (r"subprocess\.Popen\s*\(.*shell\s*=\s*True", 0.85, "Shell=True enables command injection"),
            (r"os\.system\s*\(", 0.90, "os.system() is vulnerable to command injection"),
            (r"os\.popen\s*\(", 0.85, "os.popen() is vulnerable to command injection"),
            (r"__import__\s*\(\s*['\"].*['\"]\s*\)", 0.60, "Dynamic import may lead to code injection"),
        ],
    },
    {
        "category": OwaspCategory.CRYPTOGRAPHIC_FAILURES,
        "patterns": [
            (r"(password|passwd|secret|api_key|token)\s*=\s*['\"][^'\"]{3,}['\"]", 0.85, "Hardcoded secret detected"),
            (r"md5\s*\(", 0.90, "MD5 is cryptographically broken. Use SHA-256 or better"),
            (r"sha1\s*\(", 0.80, "SHA-1 is cryptographically broken. Use SHA-256 or better"),
            (r"DES\s*\.new\s*\(", 0.90, "DES is deprecated. Use AES"),
            (r"AES\.new\s*\(.*ECB", 0.85, "ECB mode is insecure. Use CBC or GCM"),
            (r"ssl\.wrap_socket\s*\(.*ssl_version=\d+", 0.75, "Insecure SSL/TLS version"),
            (r"RC4", 0.90, "RC4 is cryptographically broken"),
        ],
    },
    {
        "category": OwaspCategory.AUTH_FAILURES,
        "patterns": [
            (r"@app\.route.*methods=\[.*'GET'.*\].*\n.*\b(password|login|auth)\b", 0.70, "Credentials exposed via GET request"),
            (r"session\.\['user'\]\s*=\s*True", 0.60, "Weak session authentication"),
            (r"token\s*=\s*['\"][a-zA-Z0-9]{1,10}['\"]", 0.70, "Suspiciously short token"),
        ],
    },
    {
        "category": OwaspCategory.SECURITY_MISCONFIGURATION,
        "patterns": [
            (r"DEBUG\s*=\s*True", 0.80, "Debug mode enabled in production"),
            (r"CORS_ORIGINS\s*=\s*\[\s*['\"]\*['\"]\s*\]", 0.85, "CORS configured with wildcard origin"),
            (r"ALLOWED_HOSTS\s*=\s*\[\s*['\"]\*['\"]\s*\]", 0.80, "ALLOWED_HOSTS set to wildcard"),
            (r"SECRET_KEY\s*=\s*['\"](default|changeme|secret)['\"]", 0.90, "Default/weak secret key"),
            (r"ssl_verify\s*=\s*False", 0.80, "SSL verification disabled"),
            (r"verify_certs\s*=\s*False", 0.80, "Certificate verification disabled"),
        ],
    },
    {
        "category": OwaspCategory.DATA_INTEGRITY_FAILURES,
        "patterns": [
            (r"pickle\.loads?\s*\(", 0.85, "Pickle deserialization can execute arbitrary code"),
            (r"yaml\.load\s*\(", 0.80, "yaml.load() without SafeLoader is unsafe"),
            (r"marshal\.loads?\s*\(", 0.85, "Marshal deserialization can execute arbitrary code"),
        ],
    },
    {
        "category": OwaspCategory.SSRF,
        "patterns": [
            (r"requests\.(get|post|put|delete)\s*\(\s*['\"](http|https)://.*\{", 0.75, "URL constructed from user input may enable SSRF"),
            (r"urllib\.request\.urlopen\s*\(\s*['\"].*\{", 0.75, "URL constructed from user input may enable SSRF"),
        ],
    },
    {
        "category": OwaspCategory.LOGGING_MONITORING_FAILURES,
        "patterns": [
            (r"except.*:\s*\n\s+pass", 0.85, "Silent exception catch prevents security monitoring"),
            (r"try:\s*\n.*\n.*\n\s+except:\s*\n\s+pass", 0.90, "Empty try/except block suppresses all errors"),
        ],
    },
]

SECRET_PATTERNS: list[tuple[str, str, float]] = [
    (r"(?:api[_-]?key|apikey)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]", "API Key", 0.90),
    (r"(?:secret|secret[_-]?key)\s*[:=]\s*['\"][a-zA-Z0-9_\-!@#$%^&*()]{16,}['\"]", "Secret Key", 0.90),
    (r"(?:aws[_-]?access[_-]?key[_-]?id)\s*[:=]\s*['\"]AKIA[0-9A-Z]{16}['\"]", "AWS Access Key", 0.95),
    (r"(?:aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*['\"][a-zA-Z0-9\/+]{40}['\"]", "AWS Secret Key", 0.95),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Token", 0.90),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token", 0.90),
    (r"xox[bpras]-[a-zA-Z0-9\-]{24,}", "Slack Token", 0.90),
    (r"sk-[a-zA-Z0-9]{32,}", "OpenAI API Key", 0.90),
    (r"pk-[a-zA-Z0-9]{32,}", "Stripe Publishable Key", 0.85),
    (r"sk_live_[a-zA-Z0-9]{24,}", "Stripe Secret Key", 0.95),
    (r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "Private Key", 0.98),
    (r"-----BEGIN CERTIFICATE-----", "Certificate", 0.80),
    (r"mongodb(?:\+srv)?://[^@]+@", "MongoDB Connection String with Credentials", 0.95),
    (r"postgres(?:ql)?://[^:]+:[^@]+@", "PostgreSQL Connection String with Credentials", 0.95),
    (r"redis://[^@]+@", "Redis Connection String with Password", 0.90),
    (r"JWT_SECRET\s*=\s*['\"][a-zA-Z0-9_\-]{8,}['\"]", "JWT Secret", 0.85),
]


class SecurityAnalyzer:
    def __init__(self) -> None:
        self._owasp_patterns = OWASP_PATTERNS
        self._secret_patterns = SECRET_PATTERNS
        self._dependency_cache: dict[str, list[dict[str, Any]]] = {}

    def analyze_code(
        self,
        code: str,
        file_path: Optional[str] = None,
        check_dependencies: bool = True,
    ) -> list[SecurityVulnerability]:
        vulns: list[SecurityVulnerability] = []

        owasp_vulns = self._detect_owasp_violations(code, file_path)
        vulns.extend(owasp_vulns)

        secrets = self._detect_secrets(code, file_path)
        vulns.extend(secrets)

        if check_dependencies:
            dep_vulns = self._check_dependency_vulnerabilities(file_path)
            vulns.extend(dep_vulns)

        vulns.sort(
            key=lambda v: (
                ["critical", "high", "medium", "low", "none"].index(v.severity.value)
                if v.severity.value in ["critical", "high", "medium", "low", "none"]
                else 10
            )
        )

        return vulns

    def _detect_owasp_violations(
        self, code: str, file_path: Optional[str] = None
    ) -> list[SecurityVulnerability]:
        vulns: list[SecurityVulnerability] = []

        for entry in self._owasp_patterns:
            category = entry["category"]
            for pattern, confidence, message in entry["patterns"]:
                for match in re.finditer(pattern, code, re.MULTILINE):
                    start_pos = match.start()
                    line_number = code[:start_pos].count("\n") + 1
                    lines = code.split("\n")
                    start_line = max(0, line_number - 2)
                    end_line = min(len(lines), line_number + 2)
                    snippet = "\n".join(lines[start_line:end_line])

                    cvss = self._estimate_cvss(category, message)
                    severity = self._cvss_to_severity(cvss)

                    vulns.append(
                        SecurityVulnerability(
                            title=f"OWASP {category.value}: Security Issue",
                            description=message,
                            severity=severity,
                            cvss_score=cvss,
                            owasp_category=category,
                            line_number=line_number,
                            snippet=snippet,
                            remediation=self._generate_remediation(category, message),
                            source="owasp_pattern",
                            file_path=file_path,
                            confidence=confidence,
                        )
                    )

        return vulns

    def _detect_secrets(
        self, code: str, file_path: Optional[str] = None
    ) -> list[SecurityVulnerability]:
        vulns: list[SecurityVulnerability] = []

        for pattern, secret_type, confidence in self._secret_patterns:
            for match in re.finditer(pattern, code, re.MULTILINE):
                start_pos = match.start()
                line_number = code[:start_pos].count("\n") + 1
                matched_text = match.group()

                redacted = re.sub(r"['\"][^'\"]+['\"]", "'***REDACTED***'", matched_text)
                lines = code.split("\n")
                start_line = max(0, line_number - 1)
                end_line = min(len(lines), line_number + 1)
                snippet = "\n".join(lines[start_line:end_line])

                vulns.append(
                    SecurityVulnerability(
                        title=f"Secret Exposure: {secret_type}",
                        description=f"A {secret_type} was detected in the source code. This can lead to unauthorized access if committed to version control.",
                        severity=VulnerabilitySeverity.CRITICAL,
                        cvss_score=9.0,
                        owasp_category=None,
                        line_number=line_number,
                        snippet=snippet,
                        remediation=RemediationSuggestion(
                            description=f"Remove the {secret_type} from code. Use environment variables or a secrets manager instead.",
                            effort="low",
                            priority="critical",
                            code_example="# Use environment variable instead:\nimport os\nsecret = os.environ.get('SECRET_NAME')",
                            references=[
                                "https://owasp.org/www-community/Secrets_Management_Cheat_Sheet"
                            ],
                        ),
                        source="secret_detection",
                        file_path=file_path,
                        confidence=confidence,
                    )
                )

        return vulns

    def _check_dependency_vulnerabilities(
        self, file_path: Optional[str] = None
    ) -> list[SecurityVulnerability]:
        vulns: list[SecurityVulnerability] = []

        req_files = []
        if file_path:
            base = Path(file_path).parent
            for req in ["requirements.txt", "Pipfile", "pyproject.toml", "poetry.lock"]:
                candidate = base / req
                if candidate.exists():
                    req_files.append(candidate)
        else:
            for req in ["requirements.txt", "Pipfile", "pyproject.toml", "poetry.lock"]:
                candidate = Path(req)
                if candidate.exists():
                    req_files.append(candidate)

        if not req_files:
            return vulns

        try:
            result = subprocess.run(  # nosec
                ["python", "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=60.0,
            )
            if result.returncode in (0, 1):
                try:
                    findings = json.loads(result.stdout)
                    for finding in findings:
                        vulns.append(
                            SecurityVulnerability(
                                title=f"Vulnerable dependency: {finding.get('package', 'unknown')}",
                                description=f"Package {finding.get('package', 'unknown')} "
                                f"v{finding.get('installed_version', '?')} has vulnerability: "
                                f"{finding.get('advisory', 'No details')}",
                                severity=self._cvss_to_severity(
                                    float(finding.get("cvss_score", 5.0))
                                ),
                                cvss_score=float(finding.get("cvss_score", 5.0)),
                                owasp_category=OwaspCategory.VULNERABLE_COMPONENTS,
                                cve_id=finding.get("cve"),
                                remediation=RemediationSuggestion(
                                    description=f"Upgrade {finding.get('package', 'unknown')} "
                                    f"to version {finding.get('fixed_version', 'latest')}",
                                    effort="low",
                                    priority="high",
                                    code_example=f"pip install --upgrade {finding.get('package', 'unknown')}",
                                    references=[finding.get("advisory_url", "")],
                                ),
                                source="dependency_check",
                                package_name=finding.get("package"),
                                installed_version=finding.get("installed_version"),
                                fixed_version=finding.get("fixed_version"),
                                confidence=0.8,
                            )
                        )
                except (json.JSONDecodeError, KeyError):
                    pass
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
            logger.debug("Safety tool unavailable: %s", exc)

        return vulns

    def analyze_project_dependencies(
        self, project_path: Optional[str] = None
    ) -> list[SecurityVulnerability]:
        return self._check_dependency_vulnerabilities(
            str(Path(project_path) / "requirements.txt") if project_path else None
        )

    def _estimate_cvss(self, category: OwaspCategory, message: str) -> float:
        cvss_map: dict[OwaspCategory, float] = {
            OwaspCategory.INJECTION: 8.5,
            OwaspCategory.CRYPTOGRAPHIC_FAILURES: 7.5,
            OwaspCategory.AUTH_FAILURES: 8.0,
            OwaspCategory.SECURITY_MISCONFIGURATION: 6.5,
            OwaspCategory.VULNERABLE_COMPONENTS: 7.0,
            OwaspCategory.DATA_INTEGRITY_FAILURES: 7.5,
            OwaspCategory.SSRF: 7.0,
            OwaspCategory.LOGGING_MONITORING_FAILURES: 5.0,
            OwaspCategory.BROKEN_ACCESS_CONTROL: 8.0,
            OwaspCategory.INSECURE_DESIGN: 7.0,
        }

        base = cvss_map.get(category, 5.0)

        if "hardcoded" in message.lower() or "secret" in message.lower():
            base += 1.0
        if "eval" in message.lower() or "exec" in message.lower():
            base += 1.0

        return min(10.0, base)

    def _cvss_to_severity(self, score: float) -> VulnerabilitySeverity:
        if score >= 9.0:
            return VulnerabilitySeverity.CRITICAL
        elif score >= 7.0:
            return VulnerabilitySeverity.HIGH
        elif score >= 4.0:
            return VulnerabilitySeverity.MEDIUM
        elif score > 0.0:
            return VulnerabilitySeverity.LOW
        return VulnerabilitySeverity.NONE

    def _generate_remediation(
        self, category: OwaspCategory, message: str
    ) -> RemediationSuggestion:
        remediations: dict[OwaspCategory, RemediationSuggestion] = {
            OwaspCategory.INJECTION: RemediationSuggestion(
                description="Use parameterized queries and input validation. Never concatenate user input into SQL/commands.",
                effort="medium",
                priority="high",
                code_example="# Use parameterized query:\ncursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
                references=["https://cheatsheetseries.owasp.org/cheatsheets/Query_Parameterization_Cheat_Sheet.html"],
            ),
            OwaspCategory.CRYPTOGRAPHIC_FAILURES: RemediationSuggestion(
                description="Use modern, strong cryptographic algorithms. Avoid MD5, SHA-1, and ECB mode.",
                effort="medium",
                priority="high",
                code_example="# Use strong hashing:\nimport hashlib\nhash = hashlib.sha256(data.encode()).hexdigest()",
                references=["https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html"],
            ),
            OwaspCategory.AUTH_FAILURES: RemediationSuggestion(
                description="Implement proper authentication with session management and MFA where applicable.",
                effort="high",
                priority="high",
                references=["https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html"],
            ),
            OwaspCategory.SECURITY_MISCONFIGURATION: RemediationSuggestion(
                description="Disable debug mode in production, restrict CORS, use strong secrets.",
                effort="low",
                priority="high",
                references=["https://cheatsheetseries.owasp.org/cheatsheets/Configuration_Cheat_Sheet.html"],
            ),
            OwaspCategory.DATA_INTEGRITY_FAILURES: RemediationSuggestion(
                description="Avoid unsafe deserialization. Use safe alternatives or validate input thoroughly.",
                effort="medium",
                priority="high",
                code_example="# Use safe YAML loading:\nimport yaml\ndata = yaml.safe_load(content)",
                references=["https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html"],
            ),
            OwaspCategory.VULNERABLE_COMPONENTS: RemediationSuggestion(
                description="Regularly update dependencies. Use tools like Dependabot or Snyk for automated updates.",
                effort="low",
                priority="medium",
                references=["https://owasp.org/www-project-dependency-check/"],
            ),
            OwaspCategory.SSRF: RemediationSuggestion(
                description="Validate and sanitize all URLs. Use an allowlist of permitted domains.",
                effort="medium",
                priority="high",
                references=["https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html"],
            ),
            OwaspCategory.LOGGING_MONITORING_FAILURES: RemediationSuggestion(
                description="Implement proper logging and monitoring. Never silently catch exceptions.",
                effort="low",
                priority="medium",
                code_example="# Always log exceptions:\ntry:\n    dangerous_operation()\nexcept Exception as exc:\n    logger.exception('Operation failed: %s', exc)",
                references=["https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html"],
            ),
            OwaspCategory.BROKEN_ACCESS_CONTROL: RemediationSuggestion(
                description="Implement proper access control checks on every request.",
                effort="high",
                priority="critical",
                references=["https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html"],
            ),
            OwaspCategory.INSECURE_DESIGN: RemediationSuggestion(
                description="Apply secure design principles: least privilege, defense in depth, secure defaults.",
                effort="high",
                priority="high",
                references=["https://owasp.org/www-community/Security_by_Design_Principles"],
            ),
        }

        default = RemediationSuggestion(
            description=f"Review and fix the security issue: {message}",
            effort="medium",
            priority="medium",
        )

        return remediations.get(category, default)

    def get_cvss_score(self, vuln: SecurityVulnerability) -> float:
        return vuln.cvss_score

    def get_owasp_category(self, vuln: SecurityVulnerability) -> Optional[OwaspCategory]:
        return vuln.owasp_category

    def get_remediation(self, vuln: SecurityVulnerability) -> Optional[str]:
        if vuln.remediation:
            return vuln.remediation.description
        return None

    def generate_security_report(
        self, vulns: list[SecurityVulnerability]
    ) -> dict[str, Any]:
        severity_counts: dict[str, int] = {}
        category_counts: dict[str, int] = {}

        for v in vulns:
            severity_counts[v.severity.value] = severity_counts.get(v.severity.value, 0) + 1
            if v.owasp_category:
                category_counts[v.owasp_category.value] = category_counts.get(v.owasp_category.value, 0) + 1

        return {
            "summary": {
                "total_vulnerabilities": len(vulns),
                "critical": severity_counts.get("critical", 0),
                "high": severity_counts.get("high", 0),
                "medium": severity_counts.get("medium", 0),
                "low": severity_counts.get("low", 0),
                "average_cvss": round(
                    sum(v.cvss_score for v in vulns) / max(len(vulns), 1), 2
                ),
            },
            "by_severity": severity_counts,
            "by_owasp_category": category_counts,
            "vulnerabilities": [v.to_dict() for v in vulns],
        }
