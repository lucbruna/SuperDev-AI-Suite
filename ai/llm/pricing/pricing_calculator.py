from __future__ import annotations

from typing import Any


class PricingCalculator:
    """Calculates costs for LLM API usage."""

    def __init__(self) -> None:
        self._prices: dict[str, dict[str, dict[str, float]]] = {}

    def register_price(
        self,
        provider: str,
        model: str,
        price_per_1k_input: float,
        price_per_1k_output: float,
    ) -> None:
        if provider not in self._prices:
            self._prices[provider] = {}
        self._prices[provider][model] = {
            "input": price_per_1k_input,
            "output": price_per_1k_output,
        }

    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        prices = self._prices.get(provider, {}).get(model)
        if prices is None:
            return 0.0
        input_cost = (input_tokens / 1000) * prices["input"]
        output_cost = (output_tokens / 1000) * prices["output"]
        return round(input_cost + output_cost, 6)

    def get_price(self, provider: str, model: str) -> dict[str, float] | None:
        return self._prices.get(provider, {}).get(model)

    def list_prices(self) -> dict[str, dict[str, dict[str, float]]]:
        return dict(self._prices)

    def to_dict(self) -> dict[str, Any]:
        return {
            "providers": list(self._prices.keys()),
            "model_count": sum(len(m) for m in self._prices.values()),
        }
