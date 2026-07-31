"""
Prompt Injection Defense
"""

import re
from dataclasses import dataclass, field
from enum import Enum


class InjectionType(Enum):
    DIRECT_INJECTION = "direct_injection"
    INDIRECT_INJECTION = "indirect_injection"
    JAILBREAK = "jailbreak"
    DATA_EXFILTRATION = "data_exfiltration"
    ROLE_MANIPULATION = "role_manipulation"


@dataclass
class PromptAnalysis:
    input_text: str
    is_safe: bool
    injection_type: InjectionType | None = None
    confidence: float = 0.0
    detected_patterns: list[str] = field(default_factory=list)
    sanitized_text: str = ""


class PromptGuard:
    def __init__(self):
        self.blocked_patterns: dict[InjectionType, list[str]] = {
            InjectionType.DIRECT_INJECTION: [
                r"ignore\s+(previous|all|above)\s+instructions",
                r"you\s+are\s+now\s+a\s+",
                r"system\s*:\s*",
                r"<\|system\|>",
            ],
            InjectionType.JAILBREAK: [
                r"dan\s+mode",
                r"jailbreak",
                r"bypass\s+(all\s+)?filters",
                r"unrestricted\s+mode",
            ],
            InjectionType.DATA_EXFILTRATION: [
                r"send\s+(all\s+)?data\s+to",
                r"exfiltrate",
                r"leak\s+(the|all|your)",
            ],
            InjectionType.ROLE_MANIPULATION: [
                r"pretend\s+you\s+are",
                r"act\s+as\s+if",
                r"from\s+now\s+on\s+you",
                r"new\s+persona",
            ],
        }
        self.analysis_log: list[PromptAnalysis] = []
        self.max_input_length: int = 10000

    def analyze(self, input_text: str) -> PromptAnalysis:
        if len(input_text) > self.max_input_length:
            return PromptAnalysis(
                input_text=input_text[:100],
                is_safe=False,
                injection_type=InjectionType.DIRECT_INJECTION,
                confidence=1.0,
                detected_patterns=["exceeds_max_length"],
            )

        detected = []
        inj_type = None
        for itype, patterns in self.blocked_patterns.items():
            for pattern in patterns:
                if re.search(pattern, input_text, re.IGNORECASE):
                    detected.append(pattern)
                    inj_type = itype

        is_safe = len(detected) == 0
        confidence = min(1.0, len(detected) * 0.3) if detected else 0.0
        sanitized = self.sanitize(input_text)
        analysis = PromptAnalysis(
            input_text=input_text[:100],
            is_safe=is_safe,
            injection_type=inj_type,
            confidence=confidence,
            detected_patterns=detected,
            sanitized_text=sanitized,
        )
        self.analysis_log.append(analysis)
        return analysis

    def sanitize(self, text: str) -> str:
        sanitized = text
        for patterns in self.blocked_patterns.values():
            for pattern in patterns:
                sanitized = re.sub(pattern, "[BLOCKED]", sanitized, flags=re.IGNORECASE)
        return sanitized

    def is_safe(self, input_text: str) -> bool:
        return self.analyze(input_text).is_safe

    def add_blocked_pattern(self, injection_type: InjectionType, pattern: str) -> None:
        self.blocked_patterns.setdefault(injection_type, []).append(pattern)

    def get_recent_analyses(self, limit: int = 10) -> list[PromptAnalysis]:
        return self.analysis_log[-limit:]

    def get_threat_stats(self) -> dict[str, int]:
        stats = {}
        for analysis in self.analysis_log:
            if analysis.injection_type:
                key = analysis.injection_type.value
                stats[key] = stats.get(key, 0) + 1
        return stats

    def count(self) -> int:
        return len(self.analysis_log)
