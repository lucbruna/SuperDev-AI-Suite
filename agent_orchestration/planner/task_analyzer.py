"""Request analysis for the planner (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_protocols import tokenize

_DOMAINS = ["erp", "financeiro", "ecommerce", "app", "site", "api", "banco"]


class TaskAnalyzer:
    """Analyzes a user request into planning signals."""

    def analyze(self, request: str) -> dict:
        tokens = tokenize(request)
        length = len(tokens)
        complexity = "high" if length >= 10 else ("medium" if length >= 4
                                                  else "low")
        return {"tokens": tokens, "length": length, "complexity": complexity}

    def requirements(self, request: str) -> list[str]:
        seen: list[str] = []
        for token in tokenize(request):
            if len(token) >= 4 and token not in seen:
                seen.append(token)
                if len(seen) == 8:
                    break
        return seen

    def extract_domain(self, request: str) -> str:
        lowered = (request or "").lower()
        for domain in _DOMAINS:
            if domain in lowered:
                return domain
        return "general"
