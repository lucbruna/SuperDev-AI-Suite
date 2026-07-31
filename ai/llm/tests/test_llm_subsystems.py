from __future__ import annotations

import pytest

from ..caching.advanced_cache import AdvancedCache
from ..compatibility.compatibility_layer import CompatibilityLayer
from ..embeddings.embedding_provider import MockEmbeddingProvider
from ..embeddings.embedding_service import EmbeddingService
from ..evaluation.evaluator import LLMEvaluator
from ..evaluation.metrics_calculator import MetricsCalculator
from ..fallback.fallback_handler import FallbackHandler
from ..llm_executor import LLMExecutor
from ..llm_logger import LLMLogger
from ..llm_metrics import LLMMetricsCollector
from ..llm_models import ProviderInfo, ProviderState
from ..llm_registry import LLMRegistry
from ..moderation.content_moderator import ContentModerator
from ..pricing.pricing_calculator import PricingCalculator
from ..prompts.prompt_manager import PromptManager
from ..prompts.prompt_template import PromptTemplate
from ..providers.mock_provider import MockProvider
from ..routing.capability_router import CapabilityRouter
from ..routing.cost_router import CostRouter
from ..routing.latency_router import LatencyRouter
from ..routing.priority_router import PriorityRouter
from ..routing.smart_router import SmartRouter
from ..routing.weighted_router import WeightedRouter
from ..streaming.stream_handler import StreamHandler
from ..telemetry.telemetry_collector import TelemetryCollector
from ..tokenizer.token_counter import TokenCounter

# ── Routing ──────────────────────────────────────────────────────

class TestCapabilityRouter:
    @pytest.mark.asyncio
    async def test_route_by_capability(self) -> None:
        router = CapabilityRouter()
        providers = [
            ProviderInfo(name="p1", model="m", capabilities=["chat"], state=ProviderState.ACTIVE),
            ProviderInfo(name="p2", model="m", capabilities=["vision"], state=ProviderState.ACTIVE),
        ]
        result = await router.route({"capabilities": ["vision"]}, providers)
        assert result == "p2"

    @pytest.mark.asyncio
    async def test_route_returns_first_if_no_capability_needed(self) -> None:
        router = CapabilityRouter()
        providers = [ProviderInfo(name="p1", model="m", state=ProviderState.ACTIVE)]
        result = await router.route({}, providers)
        assert result == "p1"


class TestLatencyRouter:
    @pytest.mark.asyncio
    async def test_route_lowest_latency(self) -> None:
        router = LatencyRouter()
        providers = [
            ProviderInfo(name="fast", model="m", latency_p50=100, state=ProviderState.ACTIVE),
            ProviderInfo(name="slow", model="m", latency_p50=500, state=ProviderState.ACTIVE),
        ]
        result = await router.route({}, providers)
        assert result == "fast"


class TestCostRouter:
    @pytest.mark.asyncio
    async def test_route_cheapest(self) -> None:
        router = CostRouter()
        providers = [
            ProviderInfo(name="cheap", model="m", cost_per_token=0.001, state=ProviderState.ACTIVE),
            ProviderInfo(name="pricey", model="m", cost_per_token=0.01, state=ProviderState.ACTIVE),
        ]
        result = await router.route({}, providers)
        assert result == "cheap"


class TestWeightedRouter:
    @pytest.mark.asyncio
    async def test_route_with_weights(self) -> None:
        router = WeightedRouter()
        router.set_weight("a", 10.0)
        router.set_weight("b", 0.1)
        providers = [
            ProviderInfo(name="a", model="m", state=ProviderState.ACTIVE),
            ProviderInfo(name="b", model="m", state=ProviderState.ACTIVE),
        ]
        results = set()
        for _ in range(50):
            r = await router.route({}, providers)
            results.add(r)
        assert "a" in results


class TestPriorityRouter:
    @pytest.mark.asyncio
    async def test_route_highest_priority(self) -> None:
        router = PriorityRouter()
        router.set_priority("high", 10)
        router.set_priority("low", 1)
        providers = [
            ProviderInfo(name="high", model="m", state=ProviderState.ACTIVE),
            ProviderInfo(name="low", model="m", state=ProviderState.ACTIVE),
        ]
        result = await router.route({}, providers)
        assert result == "high"


class TestSmartRouter:
    @pytest.mark.asyncio
    async def test_route(self) -> None:
        router = SmartRouter()
        providers = [
            ProviderInfo(name="a", model="m", latency_p50=100, cost_per_token=0.001,
                         capabilities=["chat"], state=ProviderState.ACTIVE),
            ProviderInfo(name="b", model="m", latency_p50=500, cost_per_token=0.01,
                         capabilities=[], state=ProviderState.ACTIVE),
        ]
        result = await router.route({"capabilities": ["chat"]}, providers)
        assert result == "a"


# ── Prompts ──────────────────────────────────────────────────────

class TestPromptTemplate:
    def test_render(self) -> None:
        t = PromptTemplate("Hello {name}, you are {role}!")
        result = t.render(name="Alice", role="engineer")
        assert result == "Hello Alice, you are engineer!"

    def test_save_and_load(self, tmp_path) -> None:
        path = str(tmp_path / "test_template.txt")
        t = PromptTemplate("Test {x}", name="test")
        t.save(path)
        loaded = PromptTemplate.from_file(path, name="loaded")
        assert loaded.render(x="ok") == "Test ok"


class TestPromptManager:
    def test_register_and_render(self) -> None:
        pm = PromptManager()
        pm.register("greet", "Hello {name}!")
        assert pm.render("greet", name="Bob") == "Hello Bob!"

    def test_get_nonexistent(self) -> None:
        pm = PromptManager()
        assert pm.get("nonexistent") is None


# ── Tokenizer ────────────────────────────────────────────────────

class TestTokenCounter:
    def test_count(self) -> None:
        tc = TokenCounter()
        assert tc.count("hello") == 2  # 5 chars / 4 + 1
        assert tc.count("") == 0

    def test_count_messages(self) -> None:
        tc = TokenCounter()
        msgs = [{"role": "user", "content": "hello world"}]  # 11 chars → 3 tokens
        assert tc.count_messages(msgs) > 0


# ── Embeddings ───────────────────────────────────────────────────

class TestEmbeddingService:
    @pytest.mark.asyncio
    async def test_embed_and_search(self) -> None:
        provider = MockEmbeddingProvider(dims=8)
        svc = EmbeddingService(provider)
        vec = await svc.embed("test")
        assert len(vec) == 8

        results = await svc.search("hello", ["hello world", "goodbye"], top_k=1)
        assert len(results) == 1
        assert "score" in results[0]

    def test_cosine_similarity(self) -> None:
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert EmbeddingService.cosine_similarity(a, a) == 1.0
        assert EmbeddingService.cosine_similarity(a, b) == 0.0


# ── Streaming ────────────────────────────────────────────────────

class TestStreamHandler:
    @pytest.mark.asyncio
    async def test_collect(self) -> None:
        async def fake_stream():
            yield {"content": "Hello ", "finish_reason": "continue"}
            yield {"content": "world", "finish_reason": "stop"}

        handler = StreamHandler()
        result = await handler.collect(fake_stream())
        assert result["content"] == "Hello world"
        assert result["chunk_count"] == 2


# ── Fallback ─────────────────────────────────────────────────────

class TestFallbackHandler:
    @pytest.mark.asyncio
    async def test_fallback(self) -> None:
        reg = LLMRegistry()
        reg.register(MockProvider("fallback test"))
        executor = LLMExecutor(reg, LLMMetricsCollector(), LLMLogger())

        handler = FallbackHandler()
        result = await handler.execute_with_fallback("hi", ["mock"], executor)
        assert result["success"] is True

    def test_history(self) -> None:
        handler = FallbackHandler()
        assert handler.total_attempts == 0
        assert handler.success_rate == 0.0


# ── Moderation ───────────────────────────────────────────────────

class TestContentModerator:
    def test_clean_text(self) -> None:
        mod = ContentModerator()
        result = mod.check_text("Hello, how are you?")
        assert result["flagged"] is False

    def test_flagged_text(self) -> None:
        mod = ContentModerator()
        result = mod.check_text("I hate this stupid thing")
        assert result["flagged"] is True

    def test_empty_text(self) -> None:
        mod = ContentModerator()
        result = mod.check_text("")
        assert result["flagged"] is False


# ── Evaluation ───────────────────────────────────────────────────

class TestLLMEvaluator:
    @pytest.mark.asyncio
    async def test_evaluate(self) -> None:
        evaluator = LLMEvaluator()
        scores = await evaluator.evaluate(
            "What is AI?",
            {"content": "Artificial Intelligence", "latency_ms": 100},
            criteria=["relevance", "latency"],
        )
        assert "relevance" in scores
        assert "latency" in scores

    def test_latency_score(self) -> None:
        evaluator = LLMEvaluator()
        assert evaluator.calculate_latency_score(100) == 1.0
        assert evaluator.calculate_latency_score(3000) == 0.5


class TestMetricsCalculator:
    def test_compute(self) -> None:
        mc = MetricsCalculator()
        result = mc.compute([100, 200, 300, 400, 500])
        assert result["p50"] == 200
        assert result["mean"] == 300

    def test_empty(self) -> None:
        mc = MetricsCalculator()
        result = mc.compute([])
        assert result["p50"] == 0.0


# ── Pricing ──────────────────────────────────────────────────────

class TestPricingCalculator:
    def test_calculate_cost(self) -> None:
        pc = PricingCalculator()
        pc.register_price("openai", "gpt-4", 0.03, 0.06)
        cost = pc.calculate_cost("openai", "gpt-4", 1000, 500)
        assert cost > 0

    def test_unknown_provider(self) -> None:
        pc = PricingCalculator()
        assert pc.calculate_cost("unknown", "model", 100, 100) == 0.0


# ── Telemetry ────────────────────────────────────────────────────

class TestTelemetryCollector:
    def test_record_and_get(self) -> None:
        tc = TelemetryCollector()
        tc.record_event("request", {"provider": "openai"})
        events = tc.get_events("request")
        assert len(events) == 1

    def test_summary(self) -> None:
        tc = TelemetryCollector()
        tc.record_event("a")
        tc.record_event("b")
        tc.record_event("a")
        summary = tc.get_summary()
        assert summary["a"] == 2
        assert summary["b"] == 1


# ── Advanced Cache ───────────────────────────────────────────────

class TestAdvancedCache:
    @pytest.mark.asyncio
    async def test_set_and_get(self) -> None:
        cache = AdvancedCache(max_size=10)
        await cache.set("k", {"v": 1})
        result = await cache.get("k")
        assert result == {"v": 1}

    @pytest.mark.asyncio
    async def test_eviction(self) -> None:
        cache = AdvancedCache(max_size=2)
        await cache.set("a", {"v": 1})
        await cache.set("b", {"v": 2})
        await cache.set("c", {"v": 3})
        assert await cache.get("a") is None  # evicted

    @pytest.mark.asyncio
    async def test_stats(self) -> None:
        cache = AdvancedCache()
        await cache.get("miss")  # miss
        await cache.set("k", {"v": 1})
        await cache.get("k")  # hit
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1


# ── Compatibility ────────────────────────────────────────────────

class TestCompatibilityLayer:
    def test_resolve_alias(self) -> None:
        cl = CompatibilityLayer()
        assert cl.resolve_alias("gpt-4") == "openai"
        assert cl.resolve_alias("unknown") == "unknown"

    def test_conversion(self) -> None:
        cl = CompatibilityLayer()
        converted = cl.convert_request("standard", "openai", {"prompt": "Hi", "max_tokens": 512})
        assert converted["messages"][0]["content"] == "Hi"
