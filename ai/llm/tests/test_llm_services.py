from __future__ import annotations

import pytest

from ..llm_events import LLMEventBus, LLMEventType
from ..llm_logger import LLMLogger
from ..llm_metrics import LLMMetricsCollector
from ..llm_permissions import LLMPermissions
from ..llm_registry import LLMRegistry
from ..llm_repository import LLMRepository
from ..llm_scheduler import LLMScheduler
from ..llm_security import LLMSecurity
from ..providers.mock_provider import MockProvider


class TestLLMLogger:
    def test_log_levels(self) -> None:
        logger = LLMLogger("test")
        # Should not raise
        logger.info("test", "info msg")
        logger.warning("test", "warn msg")
        logger.error("test", "err msg")
        logger.debug("test", "debug msg")


class TestLLMMetricsCollector:
    def test_record(self) -> None:
        mc = LLMMetricsCollector()
        mc.record(provider="openai", tokens_prompt=10, tokens_completion=20, success=True)
        assert mc.total_requests == 1
        assert mc.total_tokens == 30

    def test_error_rate(self) -> None:
        mc = LLMMetricsCollector()
        mc.record(provider="o", success=True)
        mc.record(provider="o", success=False)
        assert mc.error_rate == 0.5

    def test_reset(self) -> None:
        mc = LLMMetricsCollector()
        mc.record(provider="o", success=True)
        mc.reset()
        assert mc.total_requests == 0


class TestLLMEventBus:
    @pytest.mark.asyncio
    async def test_emit_and_handle(self) -> None:
        bus = LLMEventBus()
        received: list[dict] = []

        def handler(payload: dict) -> None:
            received.append(payload)

        bus.on(LLMEventType.REQUEST_START, handler)
        await bus.emit(LLMEventType.REQUEST_START, {"prompt": "hi"})

        assert len(received) == 1
        assert received[0]["event"] == "request_start"

    @pytest.mark.asyncio
    async def test_off(self) -> None:
        bus = LLMEventBus()
        calls = 0

        def handler(payload: dict) -> None:
            nonlocal calls
            calls += 1

        bus.on(LLMEventType.CACHE_HIT, handler)
        bus.off(LLMEventType.CACHE_HIT, handler)
        await bus.emit(LLMEventType.CACHE_HIT)
        assert calls == 0


class TestLLMPermissions:
    def test_grant_and_check(self) -> None:
        p = LLMPermissions()
        p.grant_provider("openai", "use")
        assert p.can_access_provider("openai", "use") is True
        assert p.can_access_provider("openai", "admin") is False

    def test_revoke(self) -> None:
        p = LLMPermissions()
        p.grant_provider("openai", "use")
        p.revoke_provider("openai", "use")
        assert p.can_access_provider("openai") is False


class TestLLMSecurity:
    @pytest.mark.asyncio
    async def test_validate_prompt_clean(self) -> None:
        sec = LLMSecurity()
        result = await sec.validate_prompt("Hello, how are you?")
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_prompt_blocked(self) -> None:
        sec = LLMSecurity()
        sec.add_blocked_pattern(r"\bhate\b")
        result = await sec.validate_prompt("I hate this")
        assert result["valid"] is False


class TestLLMRepository:
    def test_save_and_get_config(self) -> None:
        reg = LLMRegistry()
        repo = LLMRepository(reg)
        repo.save_config("openai", {"api_key": "sk-..."})
        assert repo.get_config("openai") == {"api_key": "sk-..."}

    def test_list_providers_with_configs(self) -> None:
        reg = LLMRegistry()
        reg.register(MockProvider())
        repo = LLMRepository(reg)
        result = repo.list_providers_with_configs()
        assert len(result) == 1
        assert result[0]["name"] == "mock"


class TestLLMScheduler:
    def test_schedule_and_cancel(self) -> None:
        logger = LLMLogger("test")
        sched = LLMScheduler(logger)
        task_id = sched.schedule("mock", "Hello", delay=5.0)
        assert task_id.startswith("task_")
        assert sched.pending_count == 1
        assert sched.cancel(task_id) is True
        assert sched.pending_count == 0

    def test_status(self) -> None:
        logger = LLMLogger("test")
        sched = LLMScheduler(logger)
        sched.schedule("mock", "H1", delay=1.0)
        sched.schedule("mock", "H2", delay=2.0)
        status = sched.get_status()
        assert status["pending"] == 2
