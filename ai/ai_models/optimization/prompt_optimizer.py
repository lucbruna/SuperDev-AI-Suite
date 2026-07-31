"""Prompt optimization."""

from __future__ import annotations

from typing import Any


class PromptOptimizer:
    def __init__(self) -> None:
        self._templates: dict[str, dict[str, Any]] = {}
        self._results: list[dict[str, Any]] = []

    def optimize(self, prompt: str, strategies: list[str] = None) -> dict[str, Any]:
        strategies = strategies or ["length", "clarity", "specificity"]
        optimized = prompt.strip()
        scores = {}
        for s in strategies:
            if s == "length":
                scores[s] = min(1.0, 100 / max(len(optimized), 1))
            elif s == "clarity":
                scores[s] = 0.8 if len(optimized.split()) < 50 else 0.6
            elif s == "specificity":
                scores[s] = 0.7 if any(w in optimized.lower() for w in ["specific", "exact", "precise"]) else 0.5
        result = {
            "original": prompt,
            "optimized": optimized,
            "scores": scores,
            "avg_score": sum(scores.values()) / len(scores) if scores else 0,
        }
        self._results.append(result)
        return result

    def save_template(self, name: str, prompt: str, category: str = "general") -> dict[str, Any]:
        self._templates[name] = {"prompt": prompt, "category": category, "usage_count": 0}
        return {"name": name, "saved": True}

    def get_template(self, name: str) -> str:
        return self._templates.get(name, {}).get("prompt", "")

    def list_templates(self, category: str = "") -> list[str]:
        if category:
            return [n for n, t in self._templates.items() if t["category"] == category]
        return list(self._templates.keys())

    def get_results(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._results[-limit:]

    def count(self) -> int:
        return len(self._results)
