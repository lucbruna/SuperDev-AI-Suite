"""Terraform Scanner — analyzes Terraform HCL files for security and best practices."""

from __future__ import annotations

import os
import re
import time
from typing import Any

from ..base import BaseScanner, Finding, FindingType, ScanResult, Severity


class TerraformScanner(BaseScanner):
    name = "terraform"
    description = "Analyzes Terraform HCL files for security, compliance, and best practices"

    # Terraform security checks
    TF_CHECKS: list[dict[str, Any]] = [
        {
            "rule_id": "TF-SEC-001",
            "title": "S3 bucket without encryption",
            "pattern": r'resource\s+"aws_s3_bucket"\s+"[^"]*"\s*{',
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "secondary_pattern": r"server_side_encryption_configuration",
            "recommendation": "Enable server-side encryption for S3 buckets: aws_s3_bucket_server_side_encryption_configuration",
        },
        {
            "rule_id": "TF-SEC-002",
            "title": "S3 bucket with public ACL",
            "pattern": r'resource\s+"aws_s3_bucket_public_access_block"\s+"[^"]*"\s*{[\s\S]*?block_public_acls\s*=\s*(?!true)',
            "severity": Severity.CRITICAL,
            "type": FindingType.SECURITY,
            "recommendation": "Set block_public_acls = true on S3 buckets",
        },
        {
            "rule_id": "TF-SEC-003",
            "title": "Security group with 0.0.0.0/0 ingress",
            "pattern": r'cidr_blocks\s*=\s*\[?\s*["\']0\.0\.0\.0/0["\']',
            "severity": Severity.CRITICAL,
            "type": FindingType.VULNERABILITY,
            "recommendation": "Restrict ingress CIDR to specific IP ranges, not 0.0.0.0/0",
        },
        {
            "rule_id": "TF-SEC-004",
            "title": "RDS instance publicly accessible",
            "pattern": r'resource\s+"aws_db_instance"\s+"[^"]*"\s*{[\s\S]*?publicly_accessible\s*=\s*true',
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "recommendation": "Set publicly_accessible = false for RDS instances",
        },
        {
            "rule_id": "TF-SEC-005",
            "title": "IAM user with admin policy attached",
            "pattern": r'resource\s+"aws_iam_user_policy_attachment"\s+"[^"]*"\s*{[\s\S]*?(?:AdministratorAccess|arn:aws:iam::aws:policy/AdministratorAccess)',
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "recommendation": "Grant least-privilege permissions instead of AdministratorAccess",
        },
        {
            "rule_id": "TF-SEC-006",
            "title": "EBS volume without encryption",
            "pattern": r'resource\s+"aws_ebs_volume"\s+"[^"]*"\s*{',
            "severity": Severity.MEDIUM,
            "type": FindingType.SECURITY,
            "secondary_pattern": r"encrypted\s*=\s*true",
            "recommendation": "Enable encryption for EBS volumes: encrypted = true",
        },
        {
            "rule_id": "TF-SEC-007",
            "title": "CloudTrail not enabled",
            "pattern": r'resource\s+"aws_cloudtrail"\s+"[^"]*"\s*{[\s\S]*?enable_logging\s*=\s*(?!true)',
            "severity": Severity.HIGH,
            "type": FindingType.COMPLIANCE,
            "recommendation": "Enable CloudTrail logging for API auditing",
        },
        {
            "rule_id": "TF-SEC-008",
            "title": "Sensitive data in plaintext variables",
            "pattern": r'variable\s+"[^"]*(?:password|secret|token|key|credential)"[^}]*?(?:default\s*=\s*["\'][^"\']+["\'])',
            "severity": Severity.HIGH,
            "type": FindingType.SECRET,
            "recommendation": "Use a secrets manager (AWS Secrets Manager, Vault) instead of plaintext defaults",
        },
        {
            "rule_id": "TF-SEC-009",
            "title": "No version constraint on provider",
            "pattern": r'required_providers\s*{[\s\S]*?source\s*=\s*"[^"]*"',
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "secondary_pattern": r"version\s*=",
            "recommendation": "Add version = \">= X.Y.Z\" constraint for provider reproducibility",
        },
        {
            "rule_id": "TF-BP-001",
            "title": "Hardcoded tags (no variable)",
            "pattern": r"tags\s*=\s*{[\s\S]{0,200}}(?!\s*\})",
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "recommendation": "Use locals or variables for tags instead of hardcoding values",
        },
    ]

    IGNORE_DIRS = {".git", ".terraform", "__pycache__", "node_modules"}

    async def scan(self, target: str) -> ScanResult:
        start = time.time()
        all_findings: list[Finding] = []

        path = os.path.abspath(target)
        if os.path.isfile(path):
            findings = await self._scan_tf_file(path)
            all_findings.extend(findings)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
                for fname in files:
                    if fname.endswith((".tf", ".tfvars")):
                        fpath = os.path.join(root, fname)
                        findings = await self._scan_tf_file(fpath)
                        all_findings.extend(findings)

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return ScanResult(
            scanner_name=self.name,
            target=target,
            total_findings=len(all_findings),
            findings=all_findings,
            scan_duration_ms=elapsed_ms,
        )

    async def _scan_tf_file(self, file_path: str) -> list[Finding]:
        findings: list[Finding] = []
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return findings

        fname = os.path.basename(file_path)

        for check in self.TF_CHECKS:
            primary_matches = list(re.finditer(check["pattern"], content, re.IGNORECASE))

            # Check if a secondary (mitigating) pattern exists
            has_mitigation = False
            secondary = check.get("secondary_pattern", "")
            if secondary:
                has_mitigation = bool(re.search(secondary, content, re.IGNORECASE))

            for match in primary_matches:
                # If a secondary pattern exists and is found, skip this finding
                if secondary and has_mitigation:
                    continue

                # Find the line number
                line_no = content[: match.start()].count("\n") + 1
                snippet_start = max(0, match.start() - 30)
                snippet_end = min(len(content), match.end() + 60)
                snippet = content[snippet_start:snippet_end].strip()

                findings.append(Finding(
                    rule_id=check["rule_id"],
                    title=check["title"],
                    description=f"Found in {fname}",
                    severity=check["severity"],
                    file_path=file_path,
                    line=line_no,
                    snippet=snippet[:200],
                    recommendation=check["recommendation"],
                    type=check["type"],
                ))

        return findings
