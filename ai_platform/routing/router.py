from __future__ import annotations
from typing import Any, Optional

from .selector import ModelSelector
from .routing_policy import RoutingPolicy
from .load_balancer import LoadBalancer


class AIRouter:
    def __init__(self):
        self.selector = ModelSelector()
        self.policy = RoutingPolicy()
        self.load_balancer = LoadBalancer()

    def route(self, messages: list[dict], config: Optional[dict[str, Any]] = None) -> tuple[str, str]:
        cfg = config or {}
        provider = cfg.get("provider", "")
        model = cfg.get("model", "")

        if provider and model:
            return provider, model

        context = {
            "capability": cfg.get("capability", "chat"),
            "model_size": cfg.get("model_size", "medium"),
            "cost_max": cfg.get("cost_max", float("inf")),
            "latency_max": cfg.get("latency_max", float("inf")),
            "provider": provider,
            "model": model,
        }

        policy_provider, policy_model = self.policy.evaluate(context)
        if not model:
            model = policy_model or self.selector.select(context.get("capability", "chat"), cfg)
        if not provider:
            provider = policy_provider or cfg.get("default_provider", "openai")

        return provider, model
