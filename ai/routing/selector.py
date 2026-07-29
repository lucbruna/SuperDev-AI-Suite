from __future__ import annotations

from enum import StrEnum


class SelectionStrategy(StrEnum):
    COST_FIRST = "cost_first"
    QUALITY_FIRST = "quality_first"
    LATENCY_FIRST = "latency_first"
    AUTO = "auto"


SCORING_PROFILES = {
    "cost_first": {"cost": 0.6, "quality": 0.2, "latency": 0.2},
    "quality_first": {"cost": 0.1, "quality": 0.7, "latency": 0.2},
    "latency_first": {"cost": 0.2, "quality": 0.2, "latency": 0.6},
    "auto": {"cost": 0.33, "quality": 0.33, "latency": 0.34},
}

MODEL_SCORES = {
    "gpt-4o": {"cost": 3, "quality": 10, "latency": 7},
    "gpt-4o-mini": {"cost": 8, "quality": 7, "latency": 8},
    "gpt-4-turbo": {"cost": 2, "quality": 9, "latency": 6},
    "gpt-4": {"cost": 2, "quality": 9, "latency": 5},
    "gpt-3.5-turbo": {"cost": 9, "quality": 5, "latency": 9},
    "claude-3-5-sonnet-20241022": {"cost": 3, "quality": 10, "latency": 7},
    "claude-3-opus-20240229": {"cost": 1, "quality": 10, "latency": 5},
    "claude-3-haiku-20240307": {"cost": 7, "quality": 6, "latency": 9},
    "gemini-1.5-pro": {"cost": 6, "quality": 8, "latency": 7},
    "gemini-1.5-flash": {"cost": 9, "quality": 6, "latency": 9},
    "llama3": {"cost": 10, "quality": 6, "latency": 8},
    "llama3.1": {"cost": 10, "quality": 7, "latency": 7},
    "mistral": {"cost": 10, "quality": 6, "latency": 8},
    "codestral": {"cost": 10, "quality": 7, "latency": 7},
    "deepseek-coder": {"cost": 10, "quality": 7, "latency": 7},
    "mixtral": {"cost": 10, "quality": 7, "latency": 6},
    "phi3": {"cost": 10, "quality": 5, "latency": 9},
    "gemma2": {"cost": 10, "quality": 6, "latency": 8},
    "qwen2": {"cost": 10, "quality": 6, "latency": 7},
}


class ModelSelector:
    def __init__(self, strategy: SelectionStrategy = SelectionStrategy.AUTO):
        self.strategy = strategy

    def select(self, capability: str, context: dict | None = None) -> str:
        ctx = context or {}
        strategy_name = ctx.get("strategy", self.strategy.value)
        weights = SCORING_PROFILES.get(strategy_name, SCORING_PROFILES["auto"])

        best_model = ""
        best_score = -1.0

        for model_id, scores in MODEL_SCORES.items():
            score = (
                scores.get("cost", 5) * weights["cost"]
                + scores.get("quality", 5) * weights["quality"]
                + scores.get("latency", 5) * weights["latency"]
            )
            if score > best_score:
                best_score = score
                best_model = model_id

        return best_model or "gpt-4o"
