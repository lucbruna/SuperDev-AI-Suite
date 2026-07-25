from __future__ import annotations
from pydantic import BaseModel, Field


class ModelPricing(BaseModel):
    input_per_1k: float = 0.0
    output_per_1k: float = 0.0


class ProviderCostConfig(BaseModel):
    models: dict[str, ModelPricing] = Field(default_factory=dict)


DEFAULT_PRICING: dict[str, dict[str, tuple[float, float]]] = {
    "openai": {
        "gpt-4o": (0.01, 0.03),
        "gpt-4o-mini": (0.00015, 0.0006),
        "gpt-4-turbo": (0.01, 0.03),
        "gpt-4": (0.03, 0.06),
        "gpt-3.5-turbo": (0.0005, 0.0015),
        "text-embedding-3-small": (0.00002, 0.0),
        "text-embedding-3-large": (0.00013, 0.0),
    },
    "anthropic": {
        "claude-3-5-sonnet-20241022": (0.003, 0.015),
        "claude-3-opus-20240229": (0.015, 0.075),
        "claude-3-haiku-20240307": (0.00025, 0.00125),
        "claude-2.1": (0.008, 0.024),
    },
    "gemini": {
        "gemini-1.5-pro": (0.000125, 0.000375),
        "gemini-1.5-flash": (0.000075, 0.0003),
        "gemini-1.0-pro": (0.0005, 0.0015),
    },
    "ollama": {
        "llama3": (0.0, 0.0),
        "llama3.1": (0.0, 0.0),
        "mistral": (0.0, 0.0),
        "codestral": (0.0, 0.0),
        "deepseek-coder": (0.0, 0.0),
        "mixtral": (0.0, 0.0),
        "phi3": (0.0, 0.0),
        "gemma2": (0.0, 0.0),
        "qwen2": (0.0, 0.0),
    },
}


def get_model_pricing(provider: str, model: str) -> tuple[float, float]:
    provider_pricing = DEFAULT_PRICING.get(provider, {})
    return provider_pricing.get(model, (0.0, 0.0))


def calculate_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
    input_price, output_price = get_model_pricing(provider, model)
    input_cost = (prompt_tokens / 1000) * input_price
    output_cost = (completion_tokens / 1000) * output_price
    return round(input_cost + output_cost, 6)
