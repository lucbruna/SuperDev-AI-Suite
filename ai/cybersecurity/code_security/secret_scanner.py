"""
Hardcoded Secret Scanner
"""

import re
from dataclasses import dataclass
from enum import Enum


class SecretType(Enum):
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    PRIVATE_KEY = "private_key"
    DATABASE_URL = "database_url"
    AWS_KEY = "aws_key"
    GENERIC = "generic"


@dataclass
class SecretFinding:
    secret_type: SecretType
    file_path: str
    line_number: int
    snippet: str
    confidence: float = 0.0
    entropy: float = 0.0


class SecretScanner:
    def __init__(self):
        self.patterns: dict[SecretType, list[str]] = {
            SecretType.API_KEY: [r'api[_-]?key\s*=\s*["\']([\w-]+)', r'API_KEY\s*=\s*["\']([\w-]+)'],
            SecretType.PASSWORD: [r'password\s*=\s*["\']([^"\']+)', r'passwd\s*=\s*["\']([^"\']+)'],
            SecretType.TOKEN: [r'token\s*=\s*["\']([\w.-]+)', r'access_token\s*=\s*["\']([\w.-]+)'],
            SecretType.PRIVATE_KEY: [r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"],
            SecretType.AWS_KEY: [r"AKIA[0-9A-Z]{16}"],
            SecretType.DATABASE_URL: [r"(mysql|postgresql|mongodb)://[^\s]+:[^\s]+@"],
        }
        self.findings: list[SecretFinding] = []
        self.excluded_files: set = {".env.example", "test_mock.py"}

    def scan_file(self, file_path: str, content: str) -> list[SecretFinding]:
        if any(ex in file_path for ex in self.excluded_files):
            return []
        findings = []
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for secret_type, patterns in self.patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        entropy = self._calculate_entropy(line)
                        confidence = min(1.0, entropy / 4.0)
                        finding = SecretFinding(
                            secret_type=secret_type,
                            file_path=file_path,
                            line_number=line_num,
                            snippet=line.strip()[:100],
                            confidence=confidence,
                            entropy=entropy,
                        )
                        findings.append(finding)
        self.findings.extend(findings)
        return findings

    def _calculate_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        freq = {}
        for c in text:
            freq[c] = freq.get(c, 0) + 1
        import math

        length = len(text)
        entropy = -sum((count / length) * math.log2(count / length) for count in freq.values())
        return entropy

    def get_findings(self, secret_type: SecretType = None) -> list[SecretFinding]:
        if secret_type:
            return [f for f in self.findings if f.secret_type == secret_type]
        return self.findings

    def get_high_confidence(self, threshold: float = 0.7) -> list[SecretFinding]:
        return [f for f in self.findings if f.confidence >= threshold]

    def clear_findings(self) -> None:
        self.findings.clear()

    def add_pattern(self, secret_type: SecretType, pattern: str) -> None:
        self.patterns.setdefault(secret_type, []).append(pattern)

    def exclude_file(self, file_pattern: str) -> None:
        self.excluded_files.add(file_pattern)

    def count(self) -> int:
        return len(self.findings)
