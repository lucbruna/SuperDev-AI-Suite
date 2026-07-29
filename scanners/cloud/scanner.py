"""Cloud Scanner — analyzes cloud provider configurations for security issues."""

from __future__ import annotations

import os
import re
import time
from typing import Any

from ..base import BaseScanner, Finding, FindingType, ScanResult, Severity


class CloudScanner(BaseScanner):
    name = "cloud"
    description = "Scans cloud provider configurations (AWS, Azure, GCP) for security misconfigurations"

    # Cloud security checks organized by provider
    CLOUD_CHECKS: list[dict[str, Any]] = [
        # ===== AWS Checks =====
        {
            "rule_id": "CLD-AWS-001",
            "title": "AWS S3 bucket allows public access",
            "patterns": [
                r"BlockPublicAcls\s*[=:]\s*(?:false|False|null)",
                r"IgnorePublicAcls\s*[=:]\s*(?:false|False|null)",
                r"BlockPublicPolicy\s*[=:]\s*(?:false|False|null)",
                r"RestrictPublicBuckets\s*[=:]\s*(?:false|False|null)",
            ],
            "severity": Severity.CRITICAL,
            "type": FindingType.SECURITY,
            "provider": "aws",
            "recommendation": "Set BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, and RestrictPublicBuckets to true",
        },
        {
            "rule_id": "CLD-AWS-002",
            "title": "AWS IAM policy with wildcard action (*)",
            "patterns": [
                r'Action\s*[=:]\s*["\']\*["\']',
                r'Action\s*[=:]\s*\[?\s*["\']\*["\']',
            ],
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "provider": "aws",
            "recommendation": "Grant least-privilege actions instead of * wildcard",
        },
        {
            "rule_id": "CLD-AWS-003",
            "title": "AWS Security Group with open SSH (port 22)",
            "patterns": [
                r"(?:From|To)Port\s*[=:]\s*22\b",
                r'ip_permissions[\s\S]{0,200}?from_port["\']?\s*[=:]\s*22\b',
            ],
            "severity": Severity.HIGH,
            "type": FindingType.VULNERABILITY,
            "provider": "aws",
            "recommendation": "Restrict SSH access to specific IPs, not 0.0.0.0/0",
        },
        {
            "rule_id": "CLD-AWS-004",
            "title": "AWS RDS without deletion protection",
            "patterns": [r"DeletionProtection\s*[=:]\s*(?:false|False|null)"],
            "severity": Severity.MEDIUM,
            "type": FindingType.BEST_PRACTICE,
            "provider": "aws",
            "recommendation": "Enable deletion protection on RDS instances",
        },
        # ===== Azure Checks =====
        {
            "rule_id": "CLD-AZ-001",
            "title": "Azure storage account allows public blob access",
            "patterns": [
                r"allow_blob_public_access\s*[=:]\s*(?:true|True)",
                r"AllowBlobPublicAccess\s*[=:]\s*(?:true|True)",
            ],
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "provider": "azure",
            "recommendation": "Set allow_blob_public_access = false for storage accounts",
        },
        {
            "rule_id": "CLD-AZ-002",
            "title": "Azure NSG with open RDP (port 3389)",
            "patterns": [
                r"destination_port_ranges?\s*[=:]\s*\[?\s*3389",
                r'access\s*[=:]\s*["\']Allow["\'].{0,200}?3389',
            ],
            "severity": Severity.HIGH,
            "type": FindingType.VULNERABILITY,
            "provider": "azure",
            "recommendation": "Restrict RDP access to specific IPs only",
        },
        {
            "rule_id": "CLD-AZ-003",
            "title": "Azure SQL Server with public network access",
            "patterns": [
                r"public_network_access_enabled\s*[=:]\s*(?:true|True)",
                r"PublicNetworkAccess\s*[=:]\s*(?:Enabled|true|True)",
            ],
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "provider": "azure",
            "recommendation": "Set public_network_access_enabled = false for Azure SQL",
        },
        # ===== GCP Checks =====
        {
            "rule_id": "CLD-GCP-001",
            "title": "GCP bucket with uniform access disabled",
            "patterns": [
                r"uniform_bucket_level_access\s*[=:]\s*(?:false|False)",
                r"force_destroy\s*[=:]\s*(?:true|True)",
            ],
            "severity": Severity.MEDIUM,
            "type": FindingType.SECURITY,
            "provider": "gcp",
            "recommendation": "Enable uniform bucket-level access for GCS buckets",
        },
        {
            "rule_id": "CLD-GCP-002",
            "title": "GCP firewall rule with open ingress",
            "patterns": [
                r"source_ranges\s*[=:]\s*\[?\s*[\"']0\.0\.0\.0/0[\"']",
            ],
            "severity": Severity.CRITICAL,
            "type": FindingType.VULNERABILITY,
            "provider": "gcp",
            "recommendation": "Restrict ingress firewall rules to specific source ranges",
        },
        {
            "rule_id": "CLD-GCP-003",
            "title": "GCP CloudSQL with public IP",
            "patterns": [
                r"ip_configuration[\s\S]{0,200}?ipv4_enabled\s*[=:]\s*(?:true|True)",
            ],
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "provider": "gcp",
            "recommendation": "Use private IP for CloudSQL instances",
        },
    ]

    IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".terraform"}

    SUPPORTED_EXTENSIONS = {".tf", ".tfvars", ".yaml", ".yml", ".json", ".hcl"}

    async def scan(self, target: str) -> ScanResult:
        start = time.time()
        all_findings: list[Finding] = []

        path = os.path.abspath(target)
        if os.path.isfile(path):
            findings = await self._scan_config_file(path)
            all_findings.extend(findings)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
                for fname in files:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext in self.SUPPORTED_EXTENSIONS or fname in ("main.tf",):
                        fpath = os.path.join(root, fname)
                        findings = await self._scan_config_file(fpath)
                        all_findings.extend(findings)

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return ScanResult(
            scanner_name=self.name,
            target=target,
            total_findings=len(all_findings),
            findings=all_findings,
            scan_duration_ms=elapsed_ms,
        )

    async def _scan_config_file(self, file_path: str) -> list[Finding]:
        findings: list[Finding] = []
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return findings

        fname = os.path.basename(file_path)

        for check in self.CLOUD_CHECKS:
            for pattern in check["patterns"]:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                for match in matches:
                    line_no = content[: match.start()].count("\n") + 1
                    snippet_start = max(0, match.start() - 40)
                    snippet_end = min(len(content), match.end() + 40)
                    snippet = content[snippet_start:snippet_end].strip()

                    findings.append(Finding(
                        rule_id=check["rule_id"],
                        title=check["title"],
                        description=f"Provider: {check.get('provider', 'unknown').upper()} | File: {fname}",
                        severity=check["severity"],
                        file_path=file_path,
                        line=line_no,
                        snippet=snippet[:200],
                        recommendation=check["recommendation"],
                        type=check["type"],
                        metadata={"provider": check.get("provider", "unknown")},
                    ))
                    break  # One finding per check per file

        return findings
