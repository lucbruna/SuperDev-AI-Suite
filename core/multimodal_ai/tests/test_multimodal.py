"""
Integration tests for the Multimodal AI Engine.
"""

import pytest
from ..multimodal_engine import MultimodalEngine, EngineConfig, EngineState
from ..interaction_manager import InteractionManager, ManagerConfig
from ..multimodal_config import MultimodalConfig
from ..multimodal_models import InputType, MultimodalInput
from ..multimodal_security import MultimodalSecurityManager


class TestMultimodalEngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        engine = MultimodalEngine(engine_config)
        await engine.initialize()
        assert engine.metrics.state == EngineState.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        engine = MultimodalEngine(engine_config)
        await engine.initialize()
        await engine.stop()
        assert engine.metrics.state == EngineState.STOPPED

    @pytest.mark.asyncio
    async def test_process_text_input(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        engine = MultimodalEngine(engine_config)
        await engine.initialize()
        inp = MultimodalInput(id="test-001", type=InputType.TEXT, data="Analyze sales for Q1", user_id="admin")
        result = await engine.process_input(inp)
        assert result is not None
        await engine.stop()


class TestInteractionManager:
    @pytest.mark.asyncio
    async def test_initialize_and_shutdown(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = InteractionManager(manager_config)
        await manager.initialize()
        status = await manager.get_engine_status()
        assert status["state"] == "running"
        assert manager.is_healthy() is True
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_process_input_text(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        security.access.set_user_role("admin", "admin")
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = InteractionManager(manager_config)
        await manager.initialize()
        result = await manager.process_input("Analyze inventory levels", input_type=InputType.TEXT, user_id="admin")
        assert result is not None
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_modality_stats(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = InteractionManager(manager_config)
        await manager.initialize()
        stats = await manager.get_modality_stats()
        assert isinstance(stats, dict)
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_multiple_interactions(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        security.access.set_user_role("admin", "admin")
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = InteractionManager(manager_config)
        await manager.initialize()
        session = await manager.create_session("admin")
        r1 = await manager.process_input("Show financial report", input_type=InputType.TEXT, user_id="admin", session_id=session.id)
        r2 = await manager.process_input("Analyze this image", input_type=InputType.TEXT, user_id="admin", session_id=session.id)
        history = await manager.get_interaction_history(session.id)
        assert len(history) >= 2
        await manager.shutdown()


class TestMultimodalSecurity:
    def test_privacy_mask(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        masked = security.privacy.mask_text("My email is user@example.com and phone is 123-456-7890")
        assert "EMAIL_REDACTED" in masked
        assert "PHONE_REDACTED" in masked

    def test_access_control(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        security.access.set_user_role("admin", "admin")
        assert security.access.check_access("admin", "voice", "read") is True
        assert security.access.check_access("admin", "vision", "read") is True

    def test_consent(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        security.consent.register_consent("user1", "voice", "recording", True)
        assert security.consent.check("user1", "voice", "recording") is True
        assert security.consent.check("user1", "voice", "analysis") is False

    def test_data_masking(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        security.masker.add_rule("name")
        result = security.masker.mask_data({"name": "John Doe", "email": "john@test.com", "age": 30})
        assert result["name"] != "John Doe"
        assert result["email"] == "john@test.com"


class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_multimodal_flow(self):
        config = MultimodalConfig()
        security = MultimodalSecurityManager(config)
        security.access.set_user_role("admin", "admin")
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = InteractionManager(manager_config)
        await manager.initialize()

        result = await manager.process_input("What are our sales numbers?", input_type=InputType.TEXT, user_id="admin")
        assert result is not None

        stats = await manager.get_modality_stats()
        assert "text" in stats

        status = await manager.get_engine_status()
        assert status["state"] == "running"

        healthy = manager.is_healthy()
        assert healthy is True

        await manager.shutdown()
        status2 = await manager.get_engine_status()
        assert status2["state"] == "stopped"
