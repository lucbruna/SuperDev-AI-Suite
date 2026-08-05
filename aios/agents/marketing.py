"""MarketingAgent: deterministic campaign planning and content generation."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent


class MarketingAgent(BaseAgent):
    def __init__(self, name: str = "marketing", **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="marketing",
            capabilities=["campaign_planning", "content_generation", "seo"],
            description="Plans campaigns and drafts content",
            **kwargs,
        )

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        product = input_data if isinstance(input_data, str) else str(input_data.get("product", "unknown product"))
        channels = list(context.get("channels", ["email", "social", "blog"]))
        if not channels:
            channels = ["email"]
        return {
            "product": product,
            "campaign": f"launch-{product.lower().replace(' ', '-')}",
            "headlines": [
                f"Introducing {product}",
                f"{product}: built for the future",
                f"Get {product} today",
            ],
            "channels": channels,
            "budget_split": {channel: round(100.0 / len(channels), 1) for channel in channels},
        }
