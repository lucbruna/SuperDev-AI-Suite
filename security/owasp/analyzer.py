"""OWASP Analyzer — checks source code against OWASP Top 10 vulnerability categories."""

from __future__ import annotations

import os
import re
import time
from typing import Any

from ..base import BaseCheck, SecurityFinding, SecurityReport, Severity


class OWASPAnalyzer(BaseCheck):
    name = "owasp"
    description = "OWASP Top 10 vulnerability analysis for source code"

    # OWASP Top 10 (2021) checks
    OWASP_CHECKS: list[dict[str, Any]] = [
        {
            "id": "A01",
            "name": "Broken Access Control",
            "checks": [
                {
                    "rule_id": "OWASP-A01-001",
                    "title": "Missing authorization check on API endpoint",
                    "pattern": r"@router\.(?:get|post|put|delete|patch)\b(?![\s\S]{0,200}Depends\(get_current_active_user\))",
                    "severity": Severity.CRITICAL,
                    "ext": [".py"],
                    "recommendation": "Add Depends(get_current_active_user) or similar auth dependency",
                },
                {
                    "rule_id": "OWASP-A01-002",
                    "title": "Hardcoded admin credentials",
                    "pattern": r"(?:admin|root)\s*(?::|=)\s*[\"'](?!(?:getenv|\$|os\.))[\w!@#$%^&*]{4,}",
                    "severity": Severity.HIGH,
                    "ext": [".py", ".env", ".yaml", ".json"],
                    "recommendation": "Use environment variables or a secrets manager",
                },
            ],
        },
        {
            "id": "A02",
            "name": "Cryptographic Failures",
            "checks": [
                {
                    "rule_id": "OWASP-A02-001",
                    "title": "Weak hash algorithm (MD5/SHA1)",
                    "pattern": r"(?:md5|sha1)\s*\(",
                    "severity": Severity.HIGH,
                    "ext": [".py", ".java", ".go", ".rs"],
                    "recommendation": "Use SHA-256, SHA-3, or bcrypt instead",
                },
                {
                    "rule_id": "OWASP-A02-002",
                    "title": "HTTP instead of HTTPS",
                    "pattern": r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)',
                    "severity": Severity.MEDIUM,
                    "ext": [".py", ".js", ".ts", ".yaml", ".json"],
                    "recommendation": "Use HTTPS instead of HTTP",
                },
            ],
        },
        {
            "id": "A03",
            "name": "Injection",
            "checks": [
                {
                    "rule_id": "OWASP-A03-001",
                    "title": "SQL injection risk (string formatting in query)",
                    "pattern": r'(?:execute|exec|query)\s*\(\s*[f"\'][\s\S]{0,100}%[sdf]',
                    "severity": Severity.CRITICAL,
                    "ext": [".py"],
                    "recommendation": "Use parameterized queries with placeholders (? or :name)",
                },
                {
                    "rule_id": "OWASP-A03-002",
                    "title": "Command injection risk (os.system/shell)",
                    "pattern": r'(?:os\.system|subprocess\.(?:call|Popen|run))\s*\(\s*[f"\'][\s\S]{0,50}\{',
                    "severity": Severity.CRITICAL,
                    "ext": [".py"],
                    "recommendation": "Avoid shell=True with user input. Use subprocess.run with args list.",
                },
            ],
        },
        {
            "id": "A04",
            "name": "Insecure Design",
            "checks": [
                {
                    "rule_id": "OWASP-A04-001",
                    "title": "No rate limiting on authentication endpoints",
                    "pattern": r"@router\.post\([\"']/(?:login|register|auth)",
                    "severity": Severity.MEDIUM,
                    "ext": [".py"],
                    "recommendation": "Add rate limiting to authentication endpoints",
                },
            ],
        },
        {
            "id": "A05",
            "name": "Security Misconfiguration",
            "checks": [
                {
                    "rule_id": "OWASP-A05-001",
                    "title": "Debug mode enabled in production",
                    "pattern": r'debug\s*=\s*True',
                    "severity": Severity.HIGH,
                    "ext": [".py", ".yaml", ".env"],
                    "recommendation": "Set debug=False in production environments",
                },
                {
                    "rule_id": "OWASP-A05-002",
                    "title": "CORS with wildcard origin",
                    "pattern": r"allow_origins\s*=\s*\[\s*[\"']\*[\"']\s*\]",
                    "severity": Severity.MEDIUM,
                    "ext": [".py"],
                    "recommendation": "Restrict CORS to specific origins instead of '*'",
                },
            ],
        },
        {
            "id": "A06",
            "name": "Vulnerable Components",
            "checks": [
                {
                    "rule_id": "OWASP-A06-001",
                    "title": "Known vulnerable dependency pattern",
                    "pattern": r"(?:django|flask|requests)\s*[=~>]+\s*(?:\d+\.\d+\.(?:\d+))",
                    "severity": Severity.MEDIUM,
                    "ext": [".txt", ".cfg"],
                    "recommendation": "Use `pip-audit` or `safety` to check for known vulnerabilities",
                },
            ],
        },
        {
            "id": "A07",
            "name": "Identification and Authentication Failures",
            "checks": [
                {
                    "rule_id": "OWASP-A07-001",
                    "title": "Weak password policy",
                    "pattern": r"min_length\s*[=<]\s*(?:3|4|5|6)\b",
                    "severity": Severity.MEDIUM,
                    "ext": [".py"],
                    "recommendation": "Enforce minimum password length of 8+ characters",
                },
            ],
        },
        {
            "id": "A08",
            "name": "Software and Data Integrity Failures",
            "checks": [
                {
                    "rule_id": "OWASP-A08-001",
                    "title": "Unverified dependency source",
                    "pattern": r"(?:pip install|npm install|go get)\s+(?!.*--trusted)",
                    "severity": Severity.MEDIUM,
                    "ext": [".sh", ".yml", ".yaml", "Dockerfile"],
                    "recommendation": "Pin dependency versions and verify checksums",
                },
            ],
        },
        {
            "id": "A09",
            "name": "Security Logging and Monitoring Failures",
            "checks": [
                {
                    "rule_id": "OWASP-A09-001",
                    "title": "Sensitive data in logs",
                    "pattern": r'logger\.(?:info|debug|warning)\([\s\S]{0,100}(?:password|token|secret|key|credential)',
                    "severity": Severity.HIGH,
                    "ext": [".py"],
                    "recommendation": "Never log sensitive data. Use structured logging with redaction.",
                },
            ],
        },
        {
            "id": "A10",
            "name": "Server-Side Request Forgery (SSRF)",
            "checks": [
                {
                    "rule_id": "OWASP-A10-001",
                    "title": "Unvalidated URL fetch from user input",
                    "pattern": r'(?:requests\.(?:get|post)|httpx\.(?:get|post)|urllib|aiohttp)\([\s\S]{0,30}(?:request|input|data|body)',
                    "severity": Severity.HIGH,
                    "ext": [".py"],
                    "recommendation": "Validate and sanitize URLs. Maintain a whitelist of allowed hosts.",
                },
            ],
        },
    ]

    async def analyze(self, target: str) -> SecurityReport:
        start = time.time()
        all_findings: list[SecurityFinding] = []
        path = os.path.abspath(target)

        if os.path.isfile(path):
            findings = await self._scan_file(path)
            all_findings.extend(findings)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__")]
                for fname in files:
                    fpath = os.path.join(root, fname)
                    findings = await self._scan_file(fpath)
                    all_findings.extend(findings)

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return SecurityReport(
            analyzer=self.name,
            target=target,
            total_findings=len(all_findings),
            findings=all_findings,
            scan_duration_ms=elapsed_ms,
        )

    async def _scan_file(self, file_path: str) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        ext = os.path.splitext(file_path)[1]

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return findings

        lines = content.split("\n")

        for owasp_cat in self.OWASP_CHECKS:
            for check in owasp_cat["checks"]:
                if ext not in check["ext"] and not any(fname in file_path for fname in check["ext"]):
                    continue

                for line_no, line in enumerate(lines, 1):
                    matches = re.finditer(check["pattern"], line, re.IGNORECASE)
                    for match in matches:
                        snippet = line[max(0, match.start() - 10):min(len(line), match.end() + 40)].strip()
                        findings.append(SecurityFinding(
                            rule_id=check["rule_id"],
                            title=check["title"],
                            description=f"OWASP {owasp_cat['id']}: {owasp_cat['name']}",
                            severity=check["severity"],
                            file_path=file_path,
                            line=line_no,
                            recommendation=check["recommendation"],
                            metadata={"owasp_category": owasp_cat["id"], "owasp_name": owasp_cat["name"]},
                        ))
                        break  # One finding per pattern per file

        return findings
