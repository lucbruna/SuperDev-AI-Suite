from __future__ import annotations

from typing import Any

from .llm_events import LLMEventBus, LLMEventType
from .llm_factory import LLMFactory
from .llm_logger import LLMLogger
from .llm_metrics import LLMMetricsCollector
from .llm_registry import LLMRegistry
from .llm_repository import LLMRepository
from .llm_router import LLMRouter
from .llm_scheduler import LLMScheduler
from .llm_security import LLMSecurity


class LLMManager:
    """Top-level manager for the LLM layer.

    Usage::

        from ai.llm import LLMManager

        manager = LLMManager()
        # Auto-register providers from env vars
        await manager.auto_register_providers()

        # Or manually
        provider = manager.factory.create("openai", model="gpt-4o")
        manager.registry.register(provider)
    """

    def __init__(self) -> None:
        self.logger = LLMLogger()
        self.metrics = LLMMetricsCollector()
        self.events = LLMEventBus()
        self.security = LLMSecurity()
        self.registry = LLMRegistry()
        self.repository = LLMRepository(self.registry)
        self.router = LLMRouter(self.registry)
        self.scheduler = LLMScheduler(self.logger)
        self.factory = LLMFactory()

    # ── Auto-registration ───────────────────────────────────────────

    async def auto_register_providers(self) -> list[str]:
        """Auto-detect and register providers from environment variables.

        Reads PROVIDER_CLASSES, PROVIDER_ENV_MAP, and PROVIDER_DEFAULT_MODELS
        from ``ai.llm.providers``.  Only providers whose API key env var
        is set are registered.

        Returns the list of registered provider names.
        """
        try:
            from .providers import PROVIDER_CLASSES, PROVIDER_DEFAULT_MODELS, PROVIDER_ENV_MAP
        except ImportError:
            self.logger.warning("system", "Could not import provider definitions; auto-register skipped")
            return []

        self.factory.register_all(PROVIDER_CLASSES)

        env_registered: list[str] = []
        for name, _cls in PROVIDER_CLASSES.items():
            env_config = PROVIDER_ENV_MAP.get(name, {})
            has_key = any(self._get_env(key) for key in env_config.values())
            if has_key:
                try:
                    provider = self.factory.create_with_defaults(name, PROVIDER_ENV_MAP, PROVIDER_DEFAULT_MODELS)
                    self.registry.register(provider)
                    self.logger.info(name, f"Registered provider ({provider.model()})")
                    env_registered.append(name)

                    await self.events.emit(LLMEventType.PROVIDER_REGISTERED, {
                        "provider": name,
                        "model": provider.model(),
                    })
                except Exception as exc:
                    self.logger.warning(name, f"Failed to register: {exc}")

        return env_registered

    def _get_env(self, key: str) -> str:
        import os
        return os.getenv(key, "")

    # ── Properties ──────────────────────────────────────────────────

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
            "factory_types": self.factory.list_types(),
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
