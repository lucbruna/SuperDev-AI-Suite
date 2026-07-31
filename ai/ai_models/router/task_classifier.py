"""Task classifier for routing."""
from __future__ import annotations
from typing import Any, Dict, List

class TaskClassifier:
    def __init__(self) -> None:
        self._keywords: Dict[str, List[str]] = {
            "coding": ["code", "function", "class", "api", "implement", "debug", "refactor", "python", "javascript"],
            "reasoning": ["analyze", "explain", "why", "reason", "logic", "prove", "strategy"],
            "writing": ["write", "draft", "compose", "essay", "blog", "content", "copy"],
            "vision": ["image", "photo", "visual", "diagram", "screenshot", "ocr"],
            "data": ["data", "csv", "database", "sql", "statistics", "chart", "graph"],
            "translation": ["translate", "traduzir", "localize", "i18n"],
            "summarization": ["summarize", "resumo", "summary", "brief", "overview"],
            "conversation": ["chat", "talk", "discuss", "conversation", "assist"]
        }
    def classify(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        scores: Dict[str, int] = {}
        for task_type, keywords in self._keywords.items():
            scores[task_type] = sum(1 for kw in keywords if kw in prompt_lower)
        if max(scores.values()) == 0:
            return "conversation"
        return max(scores, key=scores.get)
    def add_keywords(self, task_type: str, keywords: List[str]) -> None:
        self._keywords.setdefault(task_type, []).extend(keywords)
    def list_task_types(self) -> List[str]:
        return list(self._keywords.keys())
    def get_keywords(self, task_type: str) -> List[str]:
        return list(self._keywords.get(task_type, []))
    def confidence(self, prompt: str) -> float:
        task = self.classify(prompt)
        prompt_lower = prompt.lower()
        keywords = self._keywords.get(task, [])
        matches = sum(1 for kw in keywords if kw in prompt_lower)
        return min(matches / max(len(keywords), 1), 1.0)
