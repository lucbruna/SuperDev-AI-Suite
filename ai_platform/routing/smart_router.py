from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ai_platform.providers.base_provider import BaseProvider
from ai_platform.providers.provider_registry import ProviderRegistry


class SelectionStrategy(StrEnum):
    COST_FIRST = "cost_first"
    QUALITY_FIRST = "quality_first"
    LATENCY_FIRST = "latency_first"
    AUTO = "auto"
    BALANCED = "balanced"


class TaskType(StrEnum):
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    TEST_GENERATION = "test_generation"
    REFACTORING = "refactoring"
    ARCHITECTURE = "architecture"
    RESEARCH = "research"
    CHAT = "chat"
    REASONING = "reasoning"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"


@dataclass
class ModelScore:
    model_id: str
    provider: str
    cost_score: float = 0.0
    quality_score: float = 0.0
    latency_score: float = 0.0
    total_score: float = 0.0
    capabilities: list[str] = field(default_factory=list)
    context_window: int = 4096
    max_tokens: int = 2048


@dataclass
class RoutingContext:
    task_type: TaskType = TaskType.CHAT
    capability: str = "chat"
    model_size: str = "medium"
    cost_max: float = float("inf")
    latency_max: float = float("inf")
    provider: str = ""
    model: str = ""
    strategy: SelectionStrategy = SelectionStrategy.AUTO
    require_streaming: bool = False
    require_vision: bool = False
    require_tools: bool = False
    custom_weights: dict[str, float] = field(default_factory=dict)


@dataclass
class ProviderHealth:
    provider: str
    status: str = "unknown"
    latency_ms: float = 0.0
    error_rate: float = 0.0
    last_check: datetime | None = None
    consecutive_failures: int = 0


class SmartAIRouter:
    def __init__(self):
        self.registry = ProviderRegistry()
        self.provider_health: dict[str, ProviderHealth] = {}
        self.model_scores: dict[str, ModelScore] = {}
        self._initialize_model_scores()
        self._initialize_strategies()

    def _initialize_model_scores(self):
        scores = {
            "gpt-4o": ModelScore(
                model_id="gpt-4o", provider="openai",
                cost_score=0.3, quality_score=1.0, latency_score=0.7,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=128000, max_tokens=16384
            ),
            "gpt-4o-mini": ModelScore(
                model_id="gpt-4o-mini", provider="openai",
                cost_score=0.8, quality_score=0.7, latency_score=0.8,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=128000, max_tokens=16384
            ),
            "gpt-4-turbo": ModelScore(
                model_id="gpt-4-turbo", provider="openai",
                cost_score=0.2, quality_score=0.9, latency_score=0.6,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=128000, max_tokens=4096
            ),
            "claude-3-5-sonnet-20241022": ModelScore(
                model_id="claude-3-5-sonnet-20241022", provider="anthropic",
                cost_score=0.3, quality_score=1.0, latency_score=0.7,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=200000, max_tokens=8192
            ),
            "claude-3-opus-20240229": ModelScore(
                model_id="claude-3-opus-20240229", provider="anthropic",
                cost_score=0.1, quality_score=1.0, latency_score=0.5,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=200000, max_tokens=4096
            ),
            "claude-3-haiku-20240307": ModelScore(
                model_id="claude-3-haiku-20240307", provider="anthropic",
                cost_score=0.7, quality_score=0.6, latency_score=0.9,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=200000, max_tokens=4096
            ),
            "gemini-1.5-pro": ModelScore(
                model_id="gemini-1.5-pro", provider="gemini",
                cost_score=0.6, quality_score=0.8, latency_score=0.7,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=1000000, max_tokens=8192
            ),
            "gemini-1.5-flash": ModelScore(
                model_id="gemini-1.5-flash", provider="gemini",
                cost_score=0.9, quality_score=0.6, latency_score=0.9,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=1000000, max_tokens=8192
            ),
            "llama3": ModelScore(
                model_id="llama3", provider="ollama",
                cost_score=1.0, quality_score=0.6, latency_score=0.8,
                capabilities=["chat", "code"],
                context_window=8192, max_tokens=4096
            ),
            "llama3.1": ModelScore(
                model_id="llama3.1", provider="ollama",
                cost_score=1.0, quality_score=0.7, latency_score=0.7,
                capabilities=["chat", "code"],
                context_window=131072, max_tokens=8192
            ),
            "mistral": ModelScore(
                model_id="mistral", provider="ollama",
                cost_score=1.0, quality_score=0.6, latency_score=0.8,
                capabilities=["chat", "code"],
                context_window=8192, max_tokens=4096
            ),
            "codestral": ModelScore(
                model_id="codestral", provider="ollama",
                cost_score=1.0, quality_score=0.7, latency_score=0.7,
                capabilities=["chat", "code"],
                context_window=32768, max_tokens=8192
            ),
            "deepseek-coder": ModelScore(
                model_id="deepseek-coder", provider="ollama",
                cost_score=1.0, quality_score=0.7, latency_score=0.7,
                capabilities=["chat", "code"],
                context_window=16384, max_tokens=4096
            ),
            "mixtral": ModelScore(
                model_id="mixtral", provider="ollama",
                cost_score=1.0, quality_score=0.7, latency_score=0.6,
                capabilities=["chat", "code"],
                context_window=32768, max_tokens=4096
            ),
            "phi3": ModelScore(
                model_id="phi3", provider="ollama",
                cost_score=1.0, quality_score=0.5, latency_score=0.9,
                capabilities=["chat", "code"],
                context_window=128000, max_tokens=4096
            ),
            "gemma2": ModelScore(
                model_id="gemma2", provider="ollama",
                cost_score=1.0, quality_score=0.6, latency_score=0.8,
                capabilities=["chat", "code"],
                context_window=8192, max_tokens=4096
            ),
            "qwen2": ModelScore(
                model_id="qwen2", provider="ollama",
                cost_score=1.0, quality_score=0.6, latency_score=0.7,
                capabilities=["chat", "code"],
                context_window=32768, max_tokens=8192
            ),
            "openai/gpt-4o": ModelScore(
                model_id="openai/gpt-4o", provider="openrouter",
                cost_score=0.3, quality_score=1.0, latency_score=0.7,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=128000, max_tokens=16384
            ),
            "anthropic/claude-3.5-sonnet": ModelScore(
                model_id="anthropic/claude-3.5-sonnet", provider="openrouter",
                cost_score=0.3, quality_score=1.0, latency_score=0.7,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=200000, max_tokens=8192
            ),
            "google/gemini-pro-1.5": ModelScore(
                model_id="google/gemini-pro-1.5", provider="openrouter",
                cost_score=0.6, quality_score=0.8, latency_score=0.7,
                capabilities=["chat", "code", "vision", "tools"],
                context_window=1000000, max_tokens=8192
            ),
            "meta-llama/llama-3.1-405b": ModelScore(
                model_id="meta-llama/llama-3.1-405b", provider="openrouter",
                cost_score=0.5, quality_score=0.9, latency_score=0.5,
                capabilities=["chat", "code"],
                context_window=131072, max_tokens=8192
            ),
        }
        for score in scores.values():
            score.total_score = (score.cost_score + score.quality_score + score.latency_score) / 3
        self.model_scores = scores

    def _initialize_strategies(self):
        self.strategy_weights = {
            SelectionStrategy.COST_FIRST: {"cost": 0.6, "quality": 0.2, "latency": 0.2},
            SelectionStrategy.QUALITY_FIRST: {"cost": 0.1, "quality": 0.7, "latency": 0.2},
            SelectionStrategy.LATENCY_FIRST: {"cost": 0.2, "quality": 0.2, "latency": 0.6},
            SelectionStrategy.AUTO: {"cost": 0.33, "quality": 0.33, "latency": 0.34},
            SelectionStrategy.BALANCED: {"cost": 0.3, "quality": 0.4, "latency": 0.3},
        }

    def register_provider(self, name: str, provider_class: type[BaseProvider]):
        self.registry.register(name, provider_class)

    def register_provider_instance(self, name: str, instance: BaseProvider):
        self.registry.register_instance(name, instance)

    async def route(
        self,
        messages: list[dict],
        context: RoutingContext | None = None,
    ) -> tuple[str, str, BaseProvider]:
        ctx = context or RoutingContext()

        if ctx.provider and ctx.model:
            provider_instance = self.registry.get(ctx.provider)
            if provider_instance:
                return ctx.provider, ctx.model, provider_instance

        best_model = self._select_model(ctx)
        provider_name = self.model_scores[best_model].provider

        provider_instance = self.registry.get(provider_name)
        if not provider_instance:
            provider_instance = self.registry.get("openai")

        return provider_name, best_model, provider_instance

    def _select_model(self, ctx: RoutingContext) -> str:
        weights = self.strategy_weights.get(ctx.strategy, self.strategy_weights[SelectionStrategy.AUTO])

        if ctx.custom_weights:
            weights = {**weights, **ctx.custom_weights}

        available_models = self._get_available_models(ctx)

        if not available_models:
            return "gpt-4o-mini"

        scored_models = []
        for model_id in available_models:
            score = self.model_scores.get(model_id)
            if not score:
                continue

            if ctx.require_vision and "vision" not in score.capabilities:
                continue
            if ctx.require_tools and "tools" not in score.capabilities:
                continue
            if ctx.require_streaming:
                pass

            if score.context_window < 4096:
                continue

            health = self.provider_health.get(score.provider)
            if health and health.status == "unhealthy":
                continue

            total = (
                score.cost_score * weights.get("cost", 0.33) +
                score.quality_score * weights.get("quality", 0.33) +
                score.latency_score * weights.get("latency", 0.34)
            )

            if health and health.latency_ms > 0:
                total *= (1.0 - min(health.error_rate, 0.5))

            scored_models.append((model_id, total))

        if not scored_models:
            return "gpt-4o-mini"

        scored_models.sort(key=lambda x: x[1], reverse=True)
        return scored_models[0][0]

    def _get_available_models(self, ctx: RoutingContext) -> list[str]:
        available = []

        for provider_name in self.registry.list():
            provider = self.registry.get(provider_name)
            if not provider:
                continue

            if hasattr(provider, 'list_models'):
                try:
                    import asyncio
                    models = asyncio.run(provider.list_models())
                    for model in models:
                        if model.available and (not ctx.capability or ctx.capability in model.capabilities):
                            available.append(model.id)
                except Exception:
                    pass

        if not available:
            available = list(self.model_scores.keys())

        return available

    async def update_health(self, provider: str, status: str, latency_ms: float = 0, error: str = None):
        if provider not in self.provider_health:
            self.provider_health[provider] = ProviderHealth(provider=provider)

        health = self.provider_health[provider]
        health.status = status
        health.latency_ms = latency_ms
        health.last_check = datetime.now()

        if status == "unhealthy" or error:
            health.consecutive_failures += 1
        else:
            health.consecutive_failures = 0

        health.error_rate = min(health.consecutive_failures / 10.0, 1.0)

    async def get_model_info(self, model_id: str) -> ModelScore | None:
        return self.model_scores.get(model_id)

    async def list_available_models(self, task_type: TaskType = None) -> list[ModelScore]:
        models = list(self.model_scores.values())

        if task_type:
            task_capabilities = {
                TaskType.CODE_GENERATION: ["code"],
                TaskType.CODE_REVIEW: ["code"],
                TaskType.DEBUGGING: ["code"],
                TaskType.DOCUMENTATION: ["chat"],
                TaskType.TEST_GENERATION: ["code"],
                TaskType.REFACTORING: ["code"],
                TaskType.ARCHITECTURE: ["chat", "code"],
                TaskType.RESEARCH: ["chat"],
                TaskType.REASONING: ["chat"],
                TaskType.ANALYSIS: ["chat", "code"],
            }
            caps = task_capabilities.get(task_type, ["chat"])
            models = [m for m in models if any(c in m.capabilities for c in caps)]

        models.sort(key=lambda m: m.total_score, reverse=True)
        return models


smart_router = SmartAIRouter()
