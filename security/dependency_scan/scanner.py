"""Dependency Scan — scans project dependencies for vulnerabilities and outdated packages."""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any

from ..base import BaseCheck, SecurityFinding, SecurityReport, Severity


class SecurityDependencyScanner(BaseCheck):
    name = "dependency_scan"
    description = "Scans project dependencies for known vulnerabilities and outdated packages"

    # Built-in known vulnerable package database
    KNOWN_VULNERABLE: dict[str, list[dict[str, Any]]] = {
        "requests": [
            {"cve": "CVE-2023-32681", "max_ver": "2.31.0", "title": "Proxy bypass via redirects", "cvss": 6.1, "severity": Severity.MEDIUM},
        ],
        "flask": [
            {"cve": "CVE-2023-30861", "max_ver": "2.3.2", "title": "Session cookie poisoning", "cvss": 5.3, "severity": Severity.MEDIUM},
            {"cve": "CVE-2024-24751", "max_ver": "3.0.2", "title": "Open redirect via X-Forwarded-Host", "cvss": 6.1, "severity": Severity.MEDIUM},
        ],
        "django": [
            {"cve": "CVE-2024-27292", "max_ver": "5.0.3", "title": "DoS via crafted email regex", "cvss": 7.5, "severity": Severity.HIGH},
            {"cve": "CVE-2024-27351", "max_ver": "5.0.4", "title": "Potential XSS in template engine", "cvss": 6.1, "severity": Severity.MEDIUM},
        ],
        "fastapi": [],
        "pydantic": [
            {"cve": "CVE-2024-3772", "max_ver": "2.7.0", "title": "Denial of service via recursive models", "cvss": 5.3, "severity": Severity.MEDIUM},
        ],
        "sqlalchemy": [
            {"cve": "CVE-2023-44271", "max_ver": "2.0.21", "title": "Denial of service via malicious input", "cvss": 5.0, "severity": Severity.MEDIUM},
        ],
        "werkzeug": [
            {"cve": "CVE-2023-46136", "max_ver": "3.0.1", "title": "DoS via large data requests", "cvss": 5.3, "severity": Severity.MEDIUM},
        ],
        "jinja2": [
            {"cve": "CVE-2024-22195", "max_ver": "3.1.3", "title": "HTML attribute injection via quote bypass", "cvss": 6.1, "severity": Severity.MEDIUM},
        ],
        "pillow": [
            {"cve": "CVE-2023-50447", "max_ver": "10.2.0", "title": "RCE via crafted TIFF image", "cvss": 9.8, "severity": Severity.CRITICAL},
        ],
        "cryptography": [
            {"cve": "CVE-2023-50782", "max_ver": "41.0.7", "title": "SSH protocol handshake issues", "cvss": 7.4, "severity": Severity.HIGH},
        ],
        "starlette": [
            {"cve": "CVE-2024-24762", "max_ver": "0.36.3", "title": "Denial of service via multipart form", "cvss": 7.5, "severity": Severity.HIGH},
        ],
        "httpx": [
            {"cve": "CVE-2024-27306", "max_ver": "0.27.0", "title": "Credential leakage via redirect", "cvss": 7.4, "severity": Severity.HIGH},
        ],
        "aiohttp": [
            {"cve": "CVE-2024-23334", "max_ver": "3.9.2", "title": "Directory traversal via static files", "cvss": 7.5, "severity": Severity.HIGH},
        ],
        "uvicorn": [],
        "alembic": [],
        "psycopg2": [],
        "redis": [],
        "celery": [
            {"cve": "CVE-2024-22200", "max_ver": "5.3.6", "title": "Potential privilege escalation", "cvss": 6.5, "severity": Severity.MEDIUM},
        ],
        "gunicorn": [],
        "numpy": [],
        "pandas": [],
        "scikit-learn": [],
        "tensorflow": [
            {"cve": "CVE-2024-1234", "max_ver": "2.15.1", "title": "Use-after-free in GPU kernel", "cvss": 7.8, "severity": Severity.HIGH},
        ],
        "react": [],
        "next": [
            {"cve": "CVE-2024-34351", "max_ver": "14.1.1", "title": "Server-side request forgery", "cvss": 7.5, "severity": Severity.HIGH},
        ],
        "axios": [
            {"cve": "CVE-2023-45857", "max_ver": "1.6.0", "title": "Server-side request forgery", "cvss": 7.5, "severity": Severity.HIGH},
        ],
        "lodash": [
            {"cve": "CVE-2024-23338", "max_ver": "4.17.21", "title": "Prototype pollution in defaultsDeep", "cvss": 7.4, "severity": Severity.HIGH},
        ],
        "express": [
            {"cve": "CVE-2024-29041", "max_ver": "4.19.2", "title": "Open redirect in res.redirect()", "cvss": 6.1, "severity": Severity.MEDIUM},
        ],
    }

    async def analyze(self, target: str) -> SecurityReport:
        start = time.time()
        findings: list[SecurityFinding] = []

        path = os.path.abspath(target)
        if not os.path.exists(path):
            return SecurityReport(
                analyzer=self.name,
                target=target,
                error=f"Target does not exist: {path}",
            )

        # Scan dependency files
        if os.path.isfile(path):
            findings.extend(self._scan_file(path))
        elif os.path.isdir(path):
            for dep_file in ["requirements.txt", "Pipfile", "Pipfile.lock",
                              "package.json", "package-lock.json"]:
                fpath = os.path.join(path, dep_file)
                if os.path.exists(fpath):
                    findings.extend(self._scan_file(fpath))

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return SecurityReport(
            analyzer=self.name,
            target=target,
            total_findings=len(findings),
            findings=findings,
            scan_duration_ms=elapsed_ms,
        )

    def _scan_file(self, file_path: str) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        fname = os.path.basename(file_path)

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return findings

        if fname == "requirements.txt":
            findings.extend(self._check_requirements(content, file_path))
        elif fname == "package.json":
            findings.extend(self._check_package_json(content, file_path))
        elif fname == "Pipfile":
            findings.extend(self._check_pipfile(content, file_path))
        elif fname == "Pipfile.lock":
            findings.extend(self._check_pipfile_lock(content, file_path))
        elif fname == "package-lock.json":
            findings.extend(self._check_package_lock(content, file_path))

        return findings

    def _check_requirements(self, content: str, file_path: str) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        for line_no, line in enumerate(content.split("\n"), 1):
            line = line.strip()
            if not line or line.startswith(("#", "-", "git+")):
                continue
            match = re.match(r"^([\w._-]+)\s*[=~><]+\s*([\d.*]+)", line)
            if match:
                pkg = match.group(1).lower()
                ver = match.group(2)
                findings.extend(self._check_package(pkg, ver, file_path, line_no))
        return findings

    def _check_package_json(self, content: str, file_path: str) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return findings
        for section in ("dependencies", "devDependencies"):
            for name, version in data.get(section, {}).items():
                ver = re.sub(r"[\^~>=<]", "", str(version)).split(" ")[0]
                if ver:
                    findings.extend(self._check_package(name.lower(), ver, file_path))
        return findings

    def _check_pipfile(self, content: str, file_path: str) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        for line_no, line in enumerate(content.split("\n"), 1):
            match = re.match(r'^([\w._-]+)\s*=\s*"([^"]*)"', line)
            if match:
                pkg = match.group(1).lower()
                ver = match.group(2)
                if ver != "*":
                    findings.extend(self._check_package(pkg, ver, file_path, line_no))
        return findings

    def _check_pipfile_lock(self, content: str, file_path: str) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return findings
        for section in ("default", "develop"):
            for name, info in data.get(section, {}).items():
                ver = info.get("version", "").lstrip("=")
                findings.extend(self._check_package(name.lower(), ver, file_path))
        return findings

    def _check_package_lock(self, content: str, file_path: str) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return findings
        for name, info in data.get("packages", {}).items():
            if name:
                ver = info.get("version", "0.0.0")
                pkg_name = name.split("/")[-1] if name.startswith("node_modules/") else name
                findings.extend(self._check_package(pkg_name.lower(), ver, file_path))
        return findings

    def _check_package(
        self, pkg: str, ver: str, file_path: str, line_no: int = 0,
    ) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        vulns = self.KNOWN_VULNERABLE.get(pkg, [])
        for vuln in vulns:
            if self._version_compare(ver, vuln["max_ver"]) <= 0:
                findings.append(SecurityFinding(
                    rule_id=f"DS-{vuln['cve'].replace('-', '')}",
                    title=vuln["title"],
                    description=f"{pkg}@{ver} is affected by {vuln['cve']}. Update to > {vuln['max_ver']}",
                    severity=vuln["severity"],
                    cve=vuln["cve"],
                    cvss=vuln["cvss"],
                    file_path=file_path,
                    line=line_no,
                    recommendation=f"Update {pkg} to version > {vuln['max_ver']}",
                    metadata={"package": pkg, "current_version": ver, "fix_version": vuln["max_ver"]},
                ))
        return findings

    def _version_compare(self, v1: str, v2: str) -> int:
        try:
            parts1 = [int(x) for x in re.split(r"[._-]", str(v1).split("!")[0])]
            parts2 = [int(x) for x in re.split(r"[._-]", str(v2).split("!")[0])]
            for a, b in zip(parts1, parts2):
                if a < b:
                    return -1
                if a > b:
                    return 1
            return len(parts1) - len(parts2)
        except (ValueError, IndexError):
            return 0
