"""
Tests for the Legal AI Engine core components.
"""

import pytest
from datetime import datetime
from ..legal_engine import LegalEngine, EngineConfig, EngineState, EngineMetrics
from ..legal_manager import LegalManager, ManagerConfig
from ..legal_context import LegalContext
from ..legal_events import LegalEventBus, LegalEvent, EventType
from ..legal_models import (
    Contract, LegalDocument, ComplianceReport, RiskAssessment,
    AuditReport, PolicyDocument, LitigationCase, Clause,
    ContractStatus, ContractType, RiskLevel, ComplianceStatus,
    DocumentType, CaseStatus,
)
from ..legal_config import LegalConfig
from ..legal_security import LegalSecurityManager


class TestLegalEngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        config = LegalConfig()
        event_bus = LegalEventBus()
        context = LegalContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = LegalEngine(engine_config)
        await engine.initialize()
        assert engine.metrics.state == EngineState.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self):
        config = LegalConfig()
        event_bus = LegalEventBus()
        context = LegalContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = LegalEngine(engine_config)
        await engine.initialize()
        await engine.stop()
        assert engine.metrics.state == EngineState.STOPPED


class TestLegalManager:
    @pytest.mark.asyncio
    async def test_get_contract(self):
        config = LegalConfig()
        event_bus = LegalEventBus()
        context = LegalContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = LegalManager(manager_config)
        await manager.initialize()
        contract = await manager.get_contract("CT-001")
        assert contract is not None
        assert contract.id == "CT-001"
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_kpis(self):
        config = LegalConfig()
        event_bus = LegalEventBus()
        context = LegalContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = LegalManager(manager_config)
        await manager.initialize()
        kpis = await manager.get_kpis()
        assert kpis is not None
        assert len(kpis) > 0
        await manager.shutdown()


class TestLegalEventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        bus = LegalEventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.CONTRACT_RECEIVED, handler)
        event = LegalEvent(event_type=EventType.CONTRACT_RECEIVED, payload={"test": True})
        await bus.publish_nowait(event)
        assert len(received) == 1
        assert received[0].event_type == EventType.CONTRACT_RECEIVED

    def test_event_counts(self):
        bus = LegalEventBus()
        assert bus.get_event_count(EventType.CONTRACT_ANALYZED) == 0


class TestLegalSecurity:
    def test_access_control(self):
        security = LegalSecurityManager()
        security.set_user_role("legaldir1", "legal_director")
        assert security.check_access("legaldir1", "legal", "read") is True
        assert security.check_access("legaldir1", "legal", "audit") is True

    def test_encryption(self):
        security = LegalSecurityManager()
        data = {"contract_value": 1000000.0, "name": "Test"}
        encrypted = security.encrypt(data)
        assert encrypted["contract_value"] != 1000000.0
        decrypted = security.decrypt(encrypted)
        assert float(decrypted["contract_value"]) == 1000000.0

    def test_audit(self):
        security = LegalSecurityManager()
        entry = security.audit({"type": "contract_review", "user_id": "user1", "resource": "CT-001", "action": "approve"})
        assert entry["id"] is not None


class TestLegalModels:
    def test_contract(self):
        c = Contract(id="CT-001", title="Service Agreement", contract_type=ContractType.COMMERCIAL, value=500000.0)
        assert c.status == ContractStatus.DRAFT

    def test_clause(self):
        cl = Clause(id="CL-001", text="Confidentiality obligation", type="confidentiality", risk_level=RiskLevel.LOW)
        assert cl.is_standard is False

    def test_risk_assessment(self):
        ra = RiskAssessment(overall_score=25.0, risk_level=RiskLevel.LOW, financial_exposure=100000.0)
        assert ra.risk_level == RiskLevel.LOW


class TestIntegration:
    @pytest.mark.asyncio
    async def test_legal_flow(self):
        config = LegalConfig()
        event_bus = LegalEventBus()
        context = LegalContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = LegalManager(manager_config)
        await manager.initialize()

        contract = await manager.get_contract("CT-001")
        assert contract.title == "Sample Contract"

        compliance = await manager.get_compliance_report()
        assert compliance.overall_score > 0

        risk = await manager.get_risk_assessment()
        assert risk.overall_score >= 0

        health = await manager.get_legal_health_score()
        assert "score" in health

        await manager.shutdown()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
