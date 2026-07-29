"""Dependency Scanner — analyzes project dependencies for vulnerabilities and outdated packages."""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any

from ..base import BaseScanner, Finding, FindingType, ScanResult, Severity


class DependencyScanner(BaseScanner):
    name = "dependencies"
    description = "Scans project dependencies for known vulnerabilities and outdated packages"

    # Built-in known vulnerabilities (CVE database simulation)
    KNOWN_VULNERABILITIES: dict[str, list[dict[str, Any]]] = {
        "requests": [
            {
                "cve": "CVE-2023-32681",
                "max_version": "2.28.2",
                "title": "Requests vulnerable to proxy bypass",
                "severity": Severity.MEDIUM,
                "cvss": 6.1,
            },
        ],
        "flask": [
            {
                "cve": "CVE-2023-30861",
                "max_version": "2.2.5",
                "title": "Flask vulnerable to possible cookie poisoning",
                "severity": Severity.MEDIUM,
                "cvss": 5.3,
            },
        ],
        "django": [
            {
                "cve": "CVE-2024-27292",
                "max_version": "5.0.3",
                "title": "Django potential denial-of-service",
                "severity": Severity.HIGH,
                "cvss": 7.5,
            },
        ],
        "fastapi": [],
        "pydantic": [],
        "sqlalchemy": [
            {
                "cve": "CVE-2023-44271",
                "max_version": "2.0.21",
                "title": "SQLAlchemy denial-of-service via malicious input",
                "severity": Severity.MEDIUM,
                "cvss": 5.0,
            },
        ],
        "cryptography": [
            {
                "cve": "CVE-2023-50782",
                "max_version": "41.0.7",
                "title": "Cryptography vulnerable to SSH protocol issues",
                "severity": Severity.HIGH,
                "cvss": 7.4,
            },
        ],
        "werkzeug": [
            {
                "cve": "CVE-2023-46136",
                "max_version": "3.0.1",
                "title": "Werkzeug potential DoS via large requests",
                "severity": Severity.MEDIUM,
                "cvss": 5.3,
            },
        ],
    }

    VULNERABLE_PATTERNS = [
        (r"^([\w-]+)\s*[=~>]+\s*(\d[\w.]*)", "requirements.txt"),
        (r'"(?:@?[\w-]+)"\s*:\s*"\^?([\d.]+)"', "package.json"),
        (r'([\w-]+)\s*=\s*"==?([\d.]+)"', "Pipfile"),
    ]

    async def scan(self, target: str) -> ScanResult:
        start = time.time()
        all_findings: list[Finding] = []

        path = os.path.abspath(target)
        if os.path.isfile(path):
            findings = await self._scan_file(path)
            all_findings.extend(findings)
        elif os.path.isdir(path):
            dep_files = [
                "requirements.txt", "Pipfile", "Pipfile.lock",
                "package.json", "yarn.lock", "pnpm-lock.yaml",
                "go.mod", "Cargo.toml", "Gemfile", "pom.xml",
            ]
            for fname in dep_files:
                fpath = os.path.join(path, fname)
                if os.path.exists(fpath):
                    findings = await self._scan_file(fpath)
                    all_findings.extend(findings)

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return ScanResult(
            scanner_name=self.name,
            target=target,
            total_findings=len(all_findings),
            findings=all_findings,
            scan_duration_ms=elapsed_ms,
        )

    async def _scan_file(self, file_path: str) -> list[Finding]:
        findings: list[Finding] = []
        fname = os.path.basename(file_path)

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return findings

        if fname == "requirements.txt":
            findings.extend(self._parse_requirements(content, file_path))
        elif fname == "package.json":
            findings.extend(self._parse_package_json(content, file_path))
        elif fname == "Pipfile":
            findings.extend(self._parse_pipfile(content, file_path))

        return findings

    def _parse_requirements(self, content: str, file_path: str) -> list[Finding]:
        findings: list[Finding] = []
        for line_no, line in enumerate(content.split("\n"), 1):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            match = re.match(r"^([\w.-]+)\s*[=~>]+\s*([\d.]+)", line)
            if not match:
                continue
            pkg_name = match.group(1).lower()
            pkg_ver = match.group(2)
            findings.extend(self._check_package(pkg_name, pkg_ver, file_path, line_no))
        return findings

    def _parse_package_json(self, content: str, file_path: str) -> list[Finding]:
        findings: list[Finding] = []
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return findings

        for section in ("dependencies", "devDependencies"):
            deps = data.get(section, {})
            for pkg_name, version in deps.items():
                ver = re.sub(r"[\^~>=<]", "", str(version)).split(" ")[0]
                if ver:
                    findings.extend(self._check_package(pkg_name, ver, file_path))
        return findings

    def _parse_pipfile(self, content: str, file_path: str) -> list[Finding]:
        findings: list[Finding] = []
        current_pkg = ""
        for line_no, line in enumerate(content.split("\n"), 1):
            pkg_match = re.match(r'^([\w-]+)\s*=\s*"([\d.*]+)"', line)
            if pkg_match:
                current_pkg = pkg_match.group(1).lower()
                ver = pkg_match.group(2)
                if ver != "*":
                    findings.extend(self._check_package(current_pkg, ver, file_path, line_no))
        return findings

    def _check_package(
        self, pkg_name: str, pkg_ver: str, file_path: str, line_no: int = 0,
    ) -> list[Finding]:
        findings: list[Finding] = []
        pkg_name = pkg_name.lower()

        vulns = self.KNOWN_VULNERABILITIES.get(pkg_name, [])
        for vuln in vulns:
            if self._version_compare(pkg_ver, vuln["max_version"]) <= 0:
                findings.append(Finding(
                    rule_id="DEP-VULN-001",
                    title=f"{vuln['title']} ({pkg_name} {pkg_ver})",
                    description=f"Package {pkg_name}@{pkg_ver} is affected by {vuln['cve']}. Update to > {vuln['max_version']}",
                    severity=vuln["severity"],
                    file_path=file_path,
                    line=line_no,
                    snippet=f"{pkg_name}=={pkg_ver}",
                    recommendation=f"Update {pkg_name} to version > {vuln['max_version']}",
                    cve=vuln["cve"],
                    cvss_score=vuln["cvss"],
                    type=FindingType.VULNERABILITY,
                ))

        return findings

    def _version_compare(self, v1: str, v2: str) -> int:
        """Compare two version strings. Returns -1, 0, or 1."""
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
