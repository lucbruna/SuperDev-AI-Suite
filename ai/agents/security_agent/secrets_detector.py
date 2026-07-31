from __future__ import annotations

import re
from typing import Any

SECRET_PATTERNS: list[tuple[str, str, str]] = [
    (r"(?i)api.?key\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}", "API Key", "high"),
    (r"(?i)sk-[A-Za-z0-9]{32,}", "OpenAI API Key", "critical"),
    (r"(?i)AKIA[0-9A-Z]{16}", "AWS Access Key", "critical"),
    (r"(?i)-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", "Private Key", "critical"),
    (r"(?i)password[=:]\s*['\"][^'\"]{6,}", "Password", "high"),
    (r"(?i)secret[=:]\s*['\"][A-Za-z0-9_\-]{8,}", "Secret", "high"),
    (r"(?i)token[=:]\s*['\"][A-Za-z0-9_\-]{8,}", "Token", "medium"),
]


class SecretsDetector:
    """Detects secrets and credentials in code."""

    def __init__(self) -> None:
        self._patterns: dict[str, dict[str, Any]] = {}
        for pattern, name, severity in SECRET_PATTERNS:
            self._patterns[name] = {"name": name, "regex": pattern, "severity": severity}

    def scan_text(self, text: str) -> list[dict[str, Any]]:
        findings = []
        for pattern, name, severity in SECRET_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                findings.append(
                    {
                        "type": name,
                        "severity": severity,
                        "matches": len(matches),
                        "preview": matches[0][:20] + "..." if len(str(matches[0])) > 20 else matches[0],
                    }
                )
        return findings

    def add_pattern(self, name: str, regex: str, severity: str = "high") -> str:
        self._patterns[name] = {"name": name, "regex": regex, "severity": severity}
        return name

    def get_pattern(self, name: str) -> dict[str, Any] | None:
        return self._patterns.get(name)

    def list_patterns(self) -> list[dict[str, Any]]:
        return list(self._patterns.values())

    @property
    def pattern_count(self) -> int:
        return len(self._patterns)

    def scan_file(self, filepath: str) -> list[dict[str, Any]]:
        return self.scan_text(f"mock content for {filepath}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "patterns": list(self._patterns.values()),
            "pattern_count": self.pattern_count,
        }
