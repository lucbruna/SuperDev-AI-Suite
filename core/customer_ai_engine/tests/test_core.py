"""
Tests for the Customer AI Engine core components.
"""

import pytest
from datetime import datetime
from ..customer_engine import CustomerEngine, EngineConfig, EngineState, EngineMetrics
from ..experience_manager import ExperienceManager, ManagerConfig
from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus, CustomerEvent, EventType
from ..customer_models import (
    CustomerProfile, Conversation, Ticket, SentimentResult, LoyaltyTier,
    Campaign, CustomerTier, TicketPriority, TicketStatus, SentimentType,
    ChannelType, CampaignStatus,
)
from ..customer_config import CustomerConfig
from ..customer_security import CustomerSecurityManager


class TestCustomerEngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        config = CustomerConfig()
        event_bus = CustomerEventBus()
        context = CustomerContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = CustomerEngine(engine_config)
        await engine.initialize()
        assert engine.metrics.state == EngineState.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self):
        config = CustomerConfig()
        event_bus = CustomerEventBus()
        context = CustomerContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = CustomerEngine(engine_config)
        await engine.initialize()
        await engine.stop()
        assert engine.metrics.state == EngineState.STOPPED


class TestExperienceManager:
    @pytest.mark.asyncio
    async def test_get_customer_profile(self):
        config = CustomerConfig()
        event_bus = CustomerEventBus()
        context = CustomerContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = ExperienceManager(manager_config)
        await manager.initialize()
        profile = await manager.get_customer_profile("C-001")
        assert profile is not None
        assert profile.id == "C-001"
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_kpis(self):
        config = CustomerConfig()
        event_bus = CustomerEventBus()
        context = CustomerContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = ExperienceManager(manager_config)
        await manager.initialize()
        kpis = await manager.get_kpis()
        assert kpis is not None
        assert len(kpis) > 0
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_cx_health_score(self):
        config = CustomerConfig()
        event_bus = CustomerEventBus()
        context = CustomerContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = ExperienceManager(manager_config)
        await manager.initialize()
        health = await manager.get_cx_health_score()
        assert "score" in health
        assert "status" in health
        await manager.shutdown()


class TestCustomerEventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        bus = CustomerEventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.CUSTOMER_IDENTIFIED, handler)
        event = CustomerEvent(event_type=EventType.CUSTOMER_IDENTIFIED, payload={"test": True})
        await bus.publish_nowait(event)
        assert len(received) == 1
        assert received[0].event_type == EventType.CUSTOMER_IDENTIFIED

    def test_event_counts(self):
        bus = CustomerEventBus()
        assert bus.get_event_count(EventType.LEAD_CAPTURED) == 0


class TestCustomerSecurity:
    def test_access_control(self):
        security = CustomerSecurityManager()
        security.set_user_role("cxuser1", "cx_director")
        assert security.check_access("cxuser1", "customer", "read") is True
        assert security.check_access("cxuser1", "customer", "audit") is True

    def test_pii_encryption(self):
        security = CustomerSecurityManager()
        data = {"phone": "11999999999", "email": "test@company.com", "name": "Test"}
        encrypted = security.encrypt_pii(data)
        assert encrypted["phone"] != "11999999999"
        assert encrypted["name"] == "Test"
        decrypted = security.decrypt_pii(encrypted)
        assert decrypted["phone"] == "11999999999"
        assert decrypted["email"] == "test@company.com"

    def test_audit(self):
        security = CustomerSecurityManager()
        entry = security.log_access("user1", "customer_profile", "read", "granted")
        assert entry["id"] is not None


class TestCustomerModels:
    def test_customer_profile(self):
        profile = CustomerProfile(id="C-001", name="Ana Costa", email="ana@email.com")
        assert profile.tier == CustomerTier.BRONZE

    def test_ticket(self):
        ticket = Ticket(id="TK-0001", customer_id="C-001", subject="Problem")
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority == TicketPriority.MEDIUM

    def test_conversation(self):
        conv = Conversation(id="CV-001", customer_id="C-001", channel=ChannelType.CHAT)
        assert conv.status == "active"
        assert len(conv.messages) == 0

    def test_sentiment_result(self):
        sr = SentimentResult(text="Great service!", sentiment=SentimentType.POSITIVE, score=0.92, confidence=0.95)
        assert sr.sentiment == SentimentType.POSITIVE
        assert sr.score == 0.92

    def test_campaign(self):
        c = Campaign(id="CP-001", name="Summer Sale", channel=ChannelType.EMAIL)
        assert c.status == CampaignStatus.DRAFT
        assert c.recipients_count == 0


class TestIntegration:
    @pytest.mark.asyncio
    async def test_customer_flow(self):
        config = CustomerConfig()
        event_bus = CustomerEventBus()
        context = CustomerContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = ExperienceManager(manager_config)
        await manager.initialize()

        profile = await manager.get_customer_profile("C-001")
        assert profile.id == "C-001"

        kpis = await manager.get_kpis()
        assert len(kpis) == 22
        assert kpis["csat_score"] == 4.3

        health = await manager.get_cx_health_score()
        assert health["score"] > 0

        ticket = await manager.open_ticket("C-001", "Login issue", "Cannot login")
        assert ticket.customer_id == "C-001"
        assert ticket.subject == "Login issue"

        status = manager.get_engine_status()
        assert status["state"] == "running"

        healthy = manager.is_healthy()
        assert healthy is True

        await manager.shutdown()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
