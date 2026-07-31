"""Diagnostics engine."""

from __future__ import annotations

from typing import Any


class DiagnosticsEngine:
    def __init__(self) -> None:
        self._analyzers: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []

    def register_analyzer(self, name: str, analyzer: Any) -> None:
        self._analyzers[name] = analyzer

    def diagnose(self, problem: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        result = {"problem": problem, "context": context or {}, "findings": [], "recommendations": []}
        for name, analyzer in self._analyzers.items():
            if hasattr(analyzer, "analyze"):
                try:
                    finding = analyzer.analyze(problem, context or {})
                    result["findings"].append({"analyzer": name, "finding": finding})
                except Exception as e:
                    result["findings"].append({"analyzer": name, "error": str(e)})
        self._history.append(result)
        return result

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]

    def list_analyzers(self) -> list[str]:
        return list(self._analyzers.keys())
