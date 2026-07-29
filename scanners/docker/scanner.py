"""Docker Scanner — analyzes Dockerfiles and docker-compose for security and best practices."""

from __future__ import annotations

import os
import re
import time
from typing import Any

from ..base import BaseScanner, Finding, FindingType, ScanResult, Severity


class DockerScanner(BaseScanner):
    name = "docker"
    description = "Analyzes Dockerfiles and docker-compose files for security and best practices"

    RULES: list[dict[str, Any]] = [
        {
            "rule_id": "DK-SEC-001",
            "title": "Using latest tag",
            "pattern": r"FROM\s+\S+:\s*latest\b",
            "severity": Severity.MEDIUM,
            "type": FindingType.BEST_PRACTICE,
            "recommendation": "Pin a specific version tag instead of 'latest'",
        },
        {
            "rule_id": "DK-SEC-002",
            "title": "Running as root",
            "pattern": r"^FROM\s+\S+",
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "recommendation": "Add 'USER nobody' or create a non-root user",
            "check_no_user": True,
        },
        {
            "rule_id": "DK-SEC-003",
            "title": "Sensitive data in ARG/ENV",
            "pattern": r"(?:PASSWORD|SECRET|TOKEN|API_KEY|CREDENTIALS)\s*=",
            "severity": Severity.HIGH,
            "type": FindingType.SECRET,
            "recommendation": "Use Docker secrets or --build-arg with external values",
        },
        {
            "rule_id": "DK-BP-001",
            "title": "No HEALTHCHECK instruction",
            "pattern": r"^FROM\s+\S+",
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "recommendation": "Add a HEALTHCHECK instruction for container health monitoring",
            "check_no_healthcheck": True,
        },
        {
            "rule_id": "DK-BP-002",
            "title": "Using ADD instead of COPY",
            "pattern": r"^\s*ADD\s+",
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "recommendation": "Use COPY instead of ADD unless you need URL/tar extraction",
        },
        {
            "rule_id": "DK-SEC-004",
            "title": "Exposed port without EXPOSE",
            "pattern": r"",
            "severity": Severity.LOW,
            "type": FindingType.MISCONFIGURATION,
            "recommendation": "Always use EXPOSE to document container ports",
        },
        {
            "rule_id": "DK-SEC-005",
            "title": "apt-get without --no-install-recommends",
            "pattern": r"apt-get\s+install(?!.*--no-install-recommends)",
            "severity": Severity.LOW,
            "type": FindingType.PERFORMANCE,
            "recommendation": "Add --no-install-recommends to reduce image size",
        },
        {
            "rule_id": "DK-SEC-006",
            "title": "Hardcoded port mapping in compose",
            "pattern": r"ports:\s*\n\s*-\s*\"?\d+:\d+",
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "recommendation": "Consider using environment variables for port mappings",
        },
        {
            "rule_id": "DK-BP-003",
            "title": "Multi-stage build not used",
            "pattern": r"^FROM\s+\S+",
            "severity": Severity.LOW,
            "type": FindingType.PERFORMANCE,
            "recommendation": "Consider using multi-stage builds to reduce image size",
            "check_multi_stage": True,
        },
    ]

    async def scan(self, target: str) -> ScanResult:
        start = time.time()
        all_findings: list[Finding] = []

        path = os.path.abspath(target)
        if os.path.isfile(path):
            findings = await self._scan_docker_file(path)
            all_findings.extend(findings)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for fname in files:
                    ext = fname.lower()
                    if ext in ("dockerfile", "docker-compose.yml", "docker-compose.yaml", "Dockerfile"):
                        fpath = os.path.join(root, fname)
                        findings = await self._scan_docker_file(fpath)
                        all_findings.extend(findings)

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return ScanResult(
            scanner_name=self.name,
            target=target,
            total_findings=len(all_findings),
            findings=all_findings,
            scan_duration_ms=elapsed_ms,
        )

    async def _scan_docker_file(self, file_path: str) -> list[Finding]:
        findings: list[Finding] = []
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return findings

        fname = os.path.basename(file_path)
        lines = content.split("\n")

        # Check for USER instruction
        has_user = bool(re.search(r"^\s*USER\s+", content, re.MULTILINE))
        has_healthcheck = bool(re.search(r"^\s*HEALTHCHECK\s+", content, re.MULTILINE))
        from_count = len(re.findall(r"^FROM\s+", content, re.MULTILINE))

        for rule in self.RULES:
            rule_type = rule.get("type", FindingType.VULNERABILITY)

            # Special checks
            if rule.get("check_no_user") and has_user:
                continue
            if rule.get("check_no_healthcheck") and has_healthcheck:
                continue
            if rule.get("check_multi_stage") and from_count > 1:
                continue

            # Try to find pattern
            found = False
            for line_no, line in enumerate(lines, 1):
                if re.search(rule["pattern"], line, re.IGNORECASE):
                    findings.append(Finding(
                        rule_id=rule["rule_id"],
                        title=rule["title"],
                        description=f"Found in {fname}",
                        severity=rule["severity"],
                        file_path=file_path,
                        line=line_no,
                        snippet=line.strip()[:100],
                        recommendation=rule["recommendation"],
                        type=rule_type,
                    ))
                    found = True

            # For rules that check the entire file (no specific pattern match)
            if not found and rule["rule_id"] in ("DK-SEC-002", "DK-BP-001", "DK-BP-003"):
                continue  # These rules skip if the condition passes
            if not found and rule["pattern"]:
                pass  # Pattern not found in file

        return findings
