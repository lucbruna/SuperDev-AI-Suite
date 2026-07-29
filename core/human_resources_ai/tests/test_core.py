"""
Tests for the HR AI Engine core components.
"""

import pytest
from datetime import datetime
from ..hr_engine import HREngine, EngineConfig, EngineState, EngineMetrics
from ..talent_manager import TalentManager, ManagerConfig
from ..employee_context import EmployeeContext
from ..hr_events import HREventBus, HREvent, EventType
from ..hr_models import (
    CandidateProfile, Employee, PerformanceReview, OnboardingPlan,
    LearningPath, TalentProfile, CultureReport, WorkforcePlan,
    PayrollSummary, PerformanceRating, EmploymentStatus,
)
from ..hr_config import HRConfig
from ..hr_security import HRSecurityManager


class TestHREngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        config = HRConfig()
        event_bus = HREventBus()
        context = EmployeeContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = HREngine(engine_config)
        await engine.initialize()
        assert engine.metrics.state == EngineState.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self):
        config = HRConfig()
        event_bus = HREventBus()
        context = EmployeeContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = HREngine(engine_config)
        await engine.initialize()
        await engine.stop()
        assert engine.metrics.state == EngineState.STOPPED


class TestTalentManager:
    @pytest.mark.asyncio
    async def test_get_candidate_profile(self):
        config = HRConfig()
        event_bus = HREventBus()
        context = EmployeeContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = TalentManager(manager_config)
        await manager.initialize()
        profile = await manager.get_candidate_profile("C-001")
        assert profile is not None
        assert profile.match_score > 0
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_kpis(self):
        config = HRConfig()
        event_bus = HREventBus()
        context = EmployeeContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = TalentManager(manager_config)
        await manager.initialize()
        kpis = await manager.get_kpis()
        assert kpis is not None
        assert len(kpis) > 0
        await manager.shutdown()


class TestHREventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        bus = HREventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.CANDIDATE_SCREENED, handler)
        event = HREvent(event_type=EventType.CANDIDATE_SCREENED, payload={"test": True})
        await bus.publish_nowait(event)
        assert len(received) == 1
        assert received[0].event_type == EventType.CANDIDATE_SCREENED

    def test_event_counts(self):
        bus = HREventBus()
        assert bus.get_event_count(EventType.CANDIDATE_MATCHED) == 0


class TestHRSecurity:
    def test_access_control(self):
        security = HRSecurityManager()
        security.set_user_role("hrdir1", "hr_director")
        assert security.check_access("hrdir1", "hr", "read") is True
        assert security.check_access("hrdir1", "hr", "audit") is True

    def test_encryption(self):
        security = HRSecurityManager()
        data = {"salary": 85000.0, "name": "Test"}
        encrypted = security.encrypt(data)
        assert encrypted["salary"] != 85000.0
        decrypted = security.decrypt(encrypted)
        assert float(decrypted["salary"]) == 85000.0

    def test_audit(self):
        security = HRSecurityManager()
        entry = security.audit({"type": "salary_change", "user_id": "user1", "resource": "EMP-001", "action": "update"})
        assert entry["id"] is not None


class TestHRModels:
    def test_employee(self):
        emp = Employee(id="EMP-001", name="João Silva", email="joao@company.com", department="Engineering")
        assert emp.status == EmploymentStatus.ACTIVE

    def test_candidate_profile(self):
        c = CandidateProfile(id="C-001", name="Maria Souza", match_score=94.0, recommendation="advanced_to_interview")
        assert c.match_score == 94.0

    def test_performance_review(self):
        pr = PerformanceReview(id="R-001", employee_id="EMP-001", reviewer_id="MGR-001", period="2026-Q2", overall_score=85.0)
        assert pr.rating == PerformanceRating.MEETS


class TestIntegration:
    @pytest.mark.asyncio
    async def test_hr_flow(self):
        config = HRConfig()
        event_bus = HREventBus()
        context = EmployeeContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = TalentManager(manager_config)
        await manager.initialize()

        profile = await manager.get_candidate_profile("C-001")
        assert profile.match_score == 85.0

        culture = await manager.get_culture_report()
        assert culture.engagement_score == 76.0

        payroll = await manager.get_payroll_summary("monthly")
        assert payroll.total_employees == 500

        health = await manager.get_hr_health_score()
        assert "score" in health

        await manager.shutdown()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
