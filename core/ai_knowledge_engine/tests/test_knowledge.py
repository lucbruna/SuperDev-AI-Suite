"""
Integration tests for the AI Knowledge Engine.
"""

import pytest
from ..knowledge_engine import KnowledgeEngine, KnowledgeEngineConfig, KnowledgeEngineState, KnowledgeEngineMetrics
from ..knowledge_manager import KnowledgeManager, ManagerConfig
from ..knowledge_config import KnowledgeConfig
from ..knowledge_models import KnowledgeType, KnowledgeEntry
from ..knowledge_security import KnowledgeSecurityManager
from ..knowledge_events import KnowledgeEventBus
from ..knowledge_context import KnowledgeContext
from ..knowledge_logger import KnowledgeLogger
from ..knowledge_registry import KnowledgeRegistry
from ..knowledge_metrics import MetricsCollector


def _make_engine_config():
    config = KnowledgeConfig()
    event_bus = KnowledgeEventBus()
    context = KnowledgeContext()
    security = KnowledgeSecurityManager(config)
    security.access.set_user_role("system", "admin")
    logger = KnowledgeLogger()
    registry = KnowledgeRegistry()
    metrics = MetricsCollector(context)
    return KnowledgeEngineConfig(config=config, event_bus=event_bus, context=context, security=security, logger=logger, registry=registry, metrics_collector=metrics), security


class TestKnowledgeEngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        engine_config, _ = _make_engine_config()
        engine = KnowledgeEngine(engine_config)
        await engine.initialize()
        assert engine.metrics.state == KnowledgeEngineState.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self):
        engine_config, _ = _make_engine_config()
        engine = KnowledgeEngine(engine_config)
        await engine.initialize()
        await engine.stop()
        assert engine.metrics.state == KnowledgeEngineState.STOPPED

    @pytest.mark.asyncio
    async def test_store_and_search(self):
        engine_config, _ = _make_engine_config()
        engine = KnowledgeEngine(engine_config)
        await engine.initialize()
        entry = KnowledgeEntry(id="K-001", title="Test Knowledge", content="Test content", knowledge_type=KnowledgeType.EXPLICIT)
        await engine.store(entry)
        results = await engine.search("Test")
        assert len(results) > 0
        await engine.stop()


class TestKnowledgeManager:
    @pytest.mark.asyncio
    async def test_initialize_and_shutdown(self):
        engine_config, _ = _make_engine_config()
        manager = KnowledgeManager(ManagerConfig(engine_config=engine_config))
        await manager.initialize()
        assert manager.is_healthy() is True
        status = await manager.get_engine_status()
        assert status["state"] == "running"
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_search_knowledge(self):
        engine_config, _ = _make_engine_config()
        manager = KnowledgeManager(ManagerConfig(engine_config=engine_config))
        await manager.initialize()
        await manager.store_knowledge("Sales Data", "Q1 sales analysis", knowledge_type=KnowledgeType.EXPLICIT)
        results = await manager.search_knowledge("Sales")
        assert len(results) > 0
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_knowledge_stats(self):
        engine_config, _ = _make_engine_config()
        manager = KnowledgeManager(ManagerConfig(engine_config=engine_config))
        await manager.initialize()
        stats = await manager.get_knowledge_stats()
        assert stats.total_entries >= 0
        await manager.shutdown()


class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_knowledge_flow(self):
        engine_config, _ = _make_engine_config()
        manager = KnowledgeManager(ManagerConfig(engine_config=engine_config))
        await manager.initialize()

        entry = await manager.store_knowledge("Market Analysis", "Market trends 2026", knowledge_type=KnowledgeType.RESEARCH)

        results = await manager.search_knowledge("Market")
        assert len(results) > 0

        retrieved = await manager.get_knowledge(entry.id)
        assert retrieved is not None
        assert retrieved.title == "Market Analysis"

        stats = await manager.get_knowledge_stats()
        assert stats.total_entries > 0

        status = await manager.get_engine_status()
        assert status["state"] == "running"

        assert manager.is_healthy() is True

        await manager.shutdown()
