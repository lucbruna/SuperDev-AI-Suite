"""Injection detection."""

from __future__ import annotations

import re
from typing import Any


class InjectionDetector:
    def __init__(self) -> None:
        self._patterns: list[dict[str, Any]] = [
            {"name": "system_prompt", "pattern": r"(ignore|override)\s+(previous|all|system)", "severity": "high"},
            {"name": "role_manipulation", "pattern": r"(you are now|act as|pretend to be)", "severity": "medium"},
            {
                "name": "data_extraction",
                "pattern": r"(show|reveal|tell)\s+(me )?(your|the)\s+(prompt|system|instructions)",
                "severity": "high",
            },
            {"name": "jailbreak", "pattern": r"(dan|do anything now|jailbreak)", "severity": "high"},
        ]
        self._detected: list[dict[str, Any]] = []

    def detect(self, text: str) -> dict[str, Any]:
        detections = []
        for p in self._patterns:
            if re.search(p["pattern"], text, re.IGNORECASE):
                detections.append({"pattern": p["name"], "severity": p["severity"]})
        if detections:
            self._detected.append({"text": text[:100], "detections": detections})
        return {"safe": len(detections) == 0, "detections": detections}

    def add_pattern(self, name: str, pattern: str, severity: str = "medium") -> dict[str, Any]:
        p = {"name": name, "pattern": pattern, "severity": severity}
        self._patterns.append(p)
        return p

    def remove_pattern(self, name: str) -> bool:
        original = len(self._patterns)
        self._patterns = [p for p in self._patterns if p["name"] != name]
        return len(self._patterns) < original

    def get_detections(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._detected[-limit:]

    def list_patterns(self) -> list[dict[str, Any]]:
        return self._patterns

    def count(self) -> int:
        return len(self._detected)

    def clear(self) -> int:
        n = len(self._detected)
        self._detected.clear()
        return n
