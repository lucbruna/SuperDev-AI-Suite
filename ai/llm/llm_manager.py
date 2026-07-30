from __future__ import annotations

from typing import Any

from .llm_events import LLMEventBus, LLMEventType
from .llm_logger import LLMLogger
from .llm_metrics import LLMMetricsCollector
from .llm_registry import LLMRegistry
from .llm_repository import LLMRepository
from .llm_router import LLMRouter
from .llm_scheduler import LLMScheduler
from .llm_security import LLMSecurity


class LLMManager:
    """Top-level manager for the LLM layer."""

    def __init__(self) -> None:
        self.logger = LLMLogger()
        self.metrics = LLMMetricsCollector()
        self.events = LLMEventBus()
        self.security = LLMSecurity()
        self.registry = LLMRegistry()
        self.repository = LLMRepository(self.registry)
        self.router = LLMRouter(self.registry)
        self.scheduler = LLMScheduler(self.logger)

    @property
    def registered_providers(self) -> list[str]:
        return self.registry.list_names()

    @property
    def is_healthy(self) -> bool:
        return len(self.registered_providers) > 0

    async def health_check(self) -> dict[str, Any]:
        providers = self.registered_providers
        return {
            "healthy": len(providers) > 0,
            "provider_count": len(providers),
            "providers": providers,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_count": len(self.registered_providers),
            "providers": self.registered_providers,
            "metrics": self.metrics.to_dict(),
            "events": self.events.to_dict(),
            "router_strategies": [
                LLMRouter.STRATEGY_CAPABILITY,
                LLMRouter.STRATEGY_LATENCY,
                LLMRouter.STRATEGY_COST,
                LLMRouter.STRATEGY_QUALITY,
                LLMRouter.STRATEGY_AVAILABILITY,
                LLMRouter.STRATEGY_WEIGHTED,
                LLMRouter.STRATEGY_PRIORITY,
                LLMRouter.STRATEGY_SMART,
                LLMRouter.STRATEGY_FALLBACK,
            ],
        }
