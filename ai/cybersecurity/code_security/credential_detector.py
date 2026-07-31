"""
Credential Detection Engine
"""
import math
import re
from dataclasses import dataclass
from enum import Enum


class CredentialType(Enum):
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    OAUTH_SECRET = "oauth_secret"
    JWT_SECRET = "jwt_secret"
    DATABASE_CRED = "database_cred"
    SSH_CREDENTIAL = "ssh_credential"
    GENERIC = "generic"


@dataclass
class CredentialFinding:
    credential_type: CredentialType
    file_path: str
    line_number: int
    snippet: str
    entropy: float = 0.0
    is_false_positive: bool = False


class CredentialDetector:
    def __init__(self):
        self.patterns: dict[CredentialType, str] = {
            CredentialType.BASIC_AUTH: r'Basic\s+[A-Za-z0-9+/=]+',
            CredentialType.BEARER_TOKEN: r'Bearer\s+[\w.-]+',
            CredentialType.JWT_SECRET: r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+',
            CredentialType.DATABASE_CRED: r'(user|password|passwd|pwd)\s*[=:]\s*["\']([^"\']+)',
            CredentialType.SSH_CREDENTIAL: r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----',
        }
        self.findings: list[CredentialFinding] = []
        self.false_positive_patterns: list[str] = ["example", "placeholder", "test", "dummy", "xxx"]

    def detect(self, file_path: str, content: str) -> list[CredentialFinding]:
        findings = []
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for cred_type, pattern in self.patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    entropy = self._calculate_entropy(match.group())
                    is_fp = any(fp in line.lower() for fp in self.false_positive_patterns)
                    finding = CredentialFinding(credential_type=cred_type, file_path=file_path, line_number=line_num, snippet=line.strip()[:100], entropy=entropy, is_false_positive=is_fp)
                    findings.append(finding)
        self.findings.extend(findings)
        return findings

    def _calculate_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        freq = {}
        for c in text:
            freq[c] = freq.get(c, 0) + 1
        length = len(text)
        entropy = -sum((count / length) * math.log2(count / length) for count in freq.values())
        return entropy

    def get_findings(self, exclude_false_positives: bool = True) -> list[CredentialFinding]:
        if exclude_false_positives:
            return [f for f in self.findings if not f.is_false_positive]
        return self.findings

    def mark_false_positive(self, index: int) -> bool:
        if 0 <= index < len(self.findings):
            self.findings[index].is_false_positive = True
            return True
        return False

    def add_false_positive_pattern(self, pattern: str) -> None:
        self.false_positive_patterns.append(pattern)

    def clear(self) -> None:
        self.findings.clear()

    def count(self) -> int:
        return len(self.findings)
