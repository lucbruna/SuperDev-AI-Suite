"""Secrets Detector — advanced secrets detection with context analysis and validation."""

from __future__ import annotations

import hashlib
import os
import re
import time
from typing import Any

from ..base import BaseCheck, SecurityFinding, SecurityReport, Severity


class SecretsDetector(BaseCheck):
    name = "secrets_detector"
    description = "Advanced secrets detection with context analysis, entropy scoring, and validation"

    # Known fake/example patterns to ignore
    EXAMPLE_PATTERNS: list[str] = [
        r"your[-_]?(?:key|token|secret|password)",
        r"example[-_]?(?:key|token|secret)",
        r"changeme",
        r"xxxxx+",
        r"test[-_]?(?:key|token|secret|password)",
        r"placeholder",
        r"demo[-_]?(?:key|token|secret)",
        r"sample[-_]?(?:key|token|secret)",
    ]

    # Pattern groups with different severity levels
    PATTERN_GROUPS: list[dict[str, Any]] = [
        # Critical - high-confidence secrets
        {
            "group": "aws_credentials",
            "severity": Severity.CRITICAL,
            "patterns": [
                (r"(?i)aws[\s_=:]*secret[\s_=:]*access[\s_=:]*key[\s_=:]*['\"]?([A-Za-z0-9/+=]{40})['\"]?", "AWS Secret Access Key"),
                (r"(?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}", "AWS Access Key ID"),
            ],
        },
        {
            "group": "private_keys",
            "severity": Severity.CRITICAL,
            "patterns": [
                (r"-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)\s+PRIVATE\s+(?:KEY|BLOCK)-----", "Private Cryptographic Key"),
            ],
        },
        {
            "group": "auth_tokens",
            "severity": Severity.CRITICAL,
            "patterns": [
                (r"(?:ghp_|gho_|ghu_|ghs_|ghr_|github_pat_)[0-9A-Za-z_]{36,}", "GitHub Token"),
                (r"(?:xox[abopr]-[0-9a-z\-]{10,})", "Slack Token"),
                (r"(?:sk_live_|pk_live_|sk_test_|pk_test_)[0-9A-Za-z]{24,}", "Stripe API Key"),
                (r"(?:eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,})", "JWT Token"),
            ],
        },
        # High severity
        {
            "group": "database_urls",
            "severity": Severity.CRITICAL,
            "patterns": [
                (r"(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|rediss)\://[^:]+:[^@]+@", "Database URL with Credentials"),
            ],
        },
        {
            "group": "generic_secrets",
            "severity": Severity.HIGH,
            "patterns": [
                (r'(?i)(?:password|passwd|pwd|secret)\s*[=:]\s*["\']([^"\'\s]{8,})["\']', "Hardcoded Password/Secret"),
                (r'(?i)(?:api[_-]?key|apikey)\s*[=:]\s*["\']?([A-Za-z0-9_\-=]{16,})["\']?', "API Key"),
                (r'(?i)(?:auth[\s_=:]*token|access[\s_=:]*token)\s*[=:]\s*["\']([A-Za-z0-9_\-\.]{16,})["\']', "Auth/Access Token"),
            ],
        },
        {
            "group": "cloud_secrets",
            "severity": Severity.HIGH,
            "patterns": [
                (r'(?i)(?:google.*key|gcp.*key|service.*account|gcp_.*credential).*["\']?([A-Za-z0-9_\-]{30,})["\']?', "GCP Service Account"),
                (r'(?i)(?:azure.*key|azure.*conn|azure.*cred).*["\']?([A-Za-z0-9_\-+=/]{20,})["\']?', "Azure Credential"),
                (r'(?i)(?:heroku.*api|heroku.*key).*["\']?([A-Za-z0-9_\-]{20,})["\']?', "Heroku API Key"),
            ],
        },
        # Medium severity
        {
            "group": "potential_secrets",
            "severity": Severity.MEDIUM,
            "patterns": [
                (r'(?i)(?:token|secret|key|credential)\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']', "Potential Secret String"),
                (r'(?i)(?:connection[\s_]?string|conn[\s_]?string)\s*[=:]\s*["\']([^"\']{20,})["\']', "Connection String"),
                (r'(?i)(?:private[\s_]?key|secret[\s_]?key)\s*[=:]\s*["\']?([A-Za-z0-9_\-+=/]{20,})["\']?', "Potential Private Key"),
            ],
        },
    ]

    # Contextual whitelist for false positive reduction
    WHITELIST_PATHS = [
        r"__pycache__",
        r"\.git/",
        r"node_modules/",
        r"\.venv/",
        r"\.tox/",
        r"test.*/fixtures/",
        r"test.*/samples/",
        r"test.*/mocks/",
    ]

    # Entropy threshold for additional scanning
    ENTROPY_THRESHOLD = 4.2

    async def analyze(self, target: str) -> SecurityReport:
        start = time.time()
        all_findings: list[SecurityFinding] = []

        path = os.path.abspath(target)
        if os.path.isfile(path):
            findings = await self._scan_file(path)
            all_findings.extend(findings)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not any(
                    re.match(p, d) for p in self.WHITELIST_PATHS
                )]
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

        # Skip whitelisted paths
        for pattern in self.WHITELIST_PATHS:
            if re.search(pattern, file_path):
                return findings

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return findings

        lines = content.split("\n")
        fname = os.path.basename(file_path)

        # Skip known test/example files
        if fname in (
            "test_secrets.py", "test_secrets_detector.py",
            "credentials.example", ".env.example",
        ):
            return findings

        for group in self.PATTERN_GROUPS:
            for pattern, title in group["patterns"]:
                for line_no, line in enumerate(lines, 1):
                    # Skip comments
                    stripped = line.strip()
                    if stripped.startswith(("#", "//", "--", "*")):
                        continue

                    match = re.search(pattern, line)
                    if not match:
                        continue

                    # Skip example/placeholder values
                    if self._is_example_value(line):
                        continue

                    context = self._get_context(lines, line_no)
                    confidence = self._calculate_confidence(match, context, group["group"])

                    snippet_start = max(0, match.start() - 15)
                    snippet_end = min(len(line), match.end() + 15)
                    snippet = line[snippet_start:snippet_end].strip()

                    # Mask the actual secret value
                    if match.lastindex and match.group(match.lastindex):
                        masked = self._mask_value(snippet, match)
                    else:
                        masked = snippet

                    findings.append(SecurityFinding(
                        rule_id=f"SD-{group['group'].upper()}-001",
                        title=title,
                        description=f"{title} detected in {fname}:{line_no} (confidence: {confidence:.0%})",
                        severity=group["severity"],
                        file_path=file_path,
                        line=line_no,
                        recommendation=self._get_recommendation(group["group"]),
                        metadata={
                            "group": group["group"],
                            "confidence": round(confidence, 2),
                            "context": context[:120],
                        },
                    ))
                    break  # One finding per pattern per file

        # Entropy-based detection for potential missed secrets
        entropy_findings = self._check_entropy(content, file_path)
        findings.extend(entropy_findings)

        return findings

    def _is_example_value(self, line: str) -> bool:
        """Check if the value appears to be an example or placeholder."""
        for pattern in self.EXAMPLE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def _get_context(self, lines: list[str], line_no: int, window: int = 3) -> str:
        """Get surrounding context lines for analysis."""
        start = max(0, line_no - window - 1)
        end = min(len(lines), line_no + window)
        context_lines = []
        for i in range(start, end):
            prefix = ">" if i == line_no - 1 else " "
            context_lines.append(f"{prefix} {lines[i].strip()}")
        return "\n".join(context_lines)

    def _calculate_confidence(self, match: re.Match, context: str, group: str) -> float:
        """Calculate confidence score for a finding (0.0 to 1.0)."""
        confidence = 0.7  # Base confidence

        # Higher confidence for high-value groups
        if group in ("aws_credentials", "private_keys", "auth_tokens", "database_urls"):
            confidence += 0.2

        # Lower confidence if context contains test indicators
        if re.search(r"(?:test|mock|example|sample|fixture)", context, re.IGNORECASE):
            confidence -= 0.3

        # Higher confidence with assignment operators
        if match.group(0) and "=" in match.group(0):
            confidence += 0.1

        return min(max(confidence, 0.0), 1.0)

    def _mask_value(self, snippet: str, match: re.Match) -> str:
        """Mask the secret value in the snippet."""
        if match.lastindex:
            start, end = match.start(match.lastindex), match.end(match.lastindex)
            value = match.group(match.lastindex)
            if len(value) > 8:
                masked = value[:4] + "****" + value[-4:]
            else:
                masked = "****"
            return snippet[:start - match.start()] + masked + snippet[end - match.start():]
        return snippet

    def _check_entropy(self, content: str, file_path: str) -> list[SecurityFinding]:
        """Check for high-entropy strings that may be undiscovered secrets."""
        findings: list[SecurityFinding] = []
        string_pattern = r'["\'][A-Za-z0-9_\-=+/]{16,64}["\']'

        for match in re.finditer(string_pattern, content):
            raw = match.group()[1:-1]
            entropy = self._shannon_entropy(raw)
            if entropy >= self.ENTROPY_THRESHOLD:
                line_no = content[: match.start()].count("\n") + 1
                findings.append(SecurityFinding(
                    rule_id="SD-ENTROPY-001",
                    title=f"High-entropy string (entropy: {entropy:.2f})",
                    description="High Shannon entropy suggests possible encoded/obfuscated secret",
                    severity=Severity.LOW,
                    file_path=file_path,
                    line=line_no,
                    recommendation="Verify this string is legitimate and not a hardcoded credential",
                    metadata={"entropy": round(entropy, 2), "length": len(raw)},
                ))
        return findings

    @staticmethod
    def _shannon_entropy(data: str) -> float:
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        for char in set(data):
            prob = data.count(char) / length
            if prob > 0:
                entropy -= prob * (prob and __import__("math").log2(prob))
        return entropy

    def _get_recommendation(self, group: str) -> str:
        recommendations = {
            "aws_credentials": "Rotate AWS credentials immediately. Use IAM roles or AWS Secrets Manager.",
            "private_keys": "Remove private keys from code. Use SSH agent or hardware security module.",
            "auth_tokens": "Revoke the token immediately. Use short-lived tokens with proper scopes.",
            "database_urls": "Use database secrets rotation. Store credentials in a vault.",
            "generic_secrets": "Move secrets to environment variables or a secrets manager.",
            "cloud_secrets": "Rotate cloud credentials. Use workload identity or managed secrets.",
            "potential_secrets": "Review and move sensitive values to environment variables.",
        }
        return recommendations.get(group, "Remove hardcoded secrets and use environment variables.")
