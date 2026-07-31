"""Tests for the agents/ subpackage (Volume 31, Fase 2)."""

from __future__ import annotations

import pytest

from agent_orchestration.agents import (AgentCapabilityRegistry, AgentEngine,
                                        AgentFactory, AgentLoader,
                                        AgentManager, AgentProfileBuilder,
                                        AgentRegistry)
from agent_orchestration.orchestrator_events import (OrchestratorEventType,
                                                     OrchestratorEvents)
from agent_orchestration.orchestrator_models import AgentStatus


class TestAgentCapabilityRegistry:
    def test_seeded_catalog(self):
        registry = AgentCapabilityRegistry()
        assert registry.get("code") is not None
        assert "test" in registry.names()

    def test_register_custom(self):
        registry = AgentCapabilityRegistry()
        capability = registry.register("data", "modelar dados", ["sql"])
        assert capability.name == "data"
        assert registry.get("data") is capability

    def test_get_missing(self):
        registry = AgentCapabilityRegistry()
        assert registry.get("nope") is None


class TestAgentProfileBuilder:
    def test_standard_coding(self):
        builder = AgentProfileBuilder()
        agent = builder.standard("coding")
        assert agent.role == "coding"
        assert agent.has_capability("code")
        assert "write.project" in agent.permissions

    def test_standard_unknown_role(self):
        builder = AgentProfileBuilder()
        agent = builder.standard("mystery")
        assert agent.role == "mystery"
        assert agent.capabilities == []
        assert agent.permissions == ["read.public"]

    def test_build_assigns_ids(self):
        builder = AgentProfileBuilder()
        agent = builder.build("Agente", objective="objetivo")
        assert agent.agent_id.startswith("agent-")
        assert agent.objective == "objetivo"


class TestAgentRegistry:
    def test_crud(self):
        registry = AgentRegistry()
        builder = AgentProfileBuilder()
        agent = builder.standard("coding")
        registry.register(agent)
        assert registry.get(agent.agent_id) is agent
        assert registry.count() == 1
        assert registry.remove(agent.agent_id)
        assert registry.count() == 0

    def test_by_role_and_capability(self):
        registry = AgentRegistry()
        builder = AgentProfileBuilder()
        registry.register(builder.standard("coding"))
        registry.register(builder.standard("testing"))
        assert len(registry.by_role("coding")) == 1
        assert len(registry.by_capability("test")) == 1

    def test_available_excludes_busy(self):
        registry = AgentRegistry()
        builder = AgentProfileBuilder()
        agent = builder.standard("coding")
        agent.status = AgentStatus.BUSY
        registry.register(agent)
        assert registry.available() == []


class TestAgentLoader:
    def test_load_from_list(self):
        loader = AgentLoader()
        agents = loader.load_from_list([
            {"name": "Dev AI", "role": "coding", "capabilities": ["code"]},
            {"name": "Test AI", "role": "testing",
             "capabilities": ["test", "code"]},
        ])
        assert len(agents) == 2
        assert agents[0].has_capability("code")
        assert agents[1].has_capability("test")

    def test_load_from_dict(self):
        loader = AgentLoader()
        agents = loader.load_from_dict({"agents": [
            {"name": "Ops AI", "role": "devops",
             "capabilities": ["devops"]}]})
        assert agents[0].has_capability("devops")


class TestAgentFactory:
    def test_create(self):
        factory = AgentFactory()
        agent = factory.create("coding")
        assert agent.has_capability("code")

    def test_create_team(self):
        factory = AgentFactory()
        agents = factory.create_team(["coding", "testing"])
        assert [agent.role for agent in agents] == ["coding", "testing"]

    def test_create_coding_team(self):
        factory = AgentFactory()
        agents = factory.create_coding_team()
        assert len(agents) == 6


class TestAgentManager:
    def test_register_publishes_event(self):
        events = OrchestratorEvents()
        manager = AgentManager(events=events)
        fired = []
        events.on(OrchestratorEventType.AGENT_REGISTERED,
                  lambda payload: fired.append(payload))
        builder = AgentProfileBuilder()
        agent = manager.register(builder.standard("coding"))
        assert len(fired) == 1
        assert fired[0]["agent_id"] == agent.agent_id

    def test_pick_agent_marks_busy(self):
        manager = AgentManager()
        builder = AgentProfileBuilder()
        agent = manager.register(builder.standard("coding"))
        picked = manager.pick_agent("code")
        assert picked is agent
        assert agent.status == AgentStatus.BUSY

    def test_pick_agent_returns_none_when_busy(self):
        manager = AgentManager()
        builder = AgentProfileBuilder()
        agent = manager.register(builder.standard("coding"))
        manager.pick_agent("code")
        assert manager.pick_agent("code") is None
        manager.release(agent.agent_id)
        assert manager.pick_agent("code") is agent

    def test_can_respects_permissions(self):
        manager = AgentManager()
        builder = AgentProfileBuilder()
        agent = manager.register(builder.standard("coding"))
        assert manager.can(agent.agent_id, "write.project")
        assert not manager.can(agent.agent_id, "deploy.project")
        assert manager.grant_permission(agent.agent_id, "deploy.project")
        assert manager.can(agent.agent_id, "deploy.project")

    def test_unregister_missing(self):
        manager = AgentManager()
        assert not manager.unregister("agent-missing")


class TestAgentEngine:
    def test_end_to_end(self):
        engine = AgentEngine()
        engine.register(engine.create("coding"))
        engine.register(engine.create("testing"))
        picked = engine.pick_agent("code")
        assert picked is not None
        assert engine.release(picked.agent_id)
        stats = engine.stats()
        assert stats["agents"] == 2
        assert stats["by_role"]["coding"] == 1

    def test_stats_metrics(self):
        engine = AgentEngine()
        engine.create_coding_team()
        stats = engine.stats()
        assert stats["agents"] == 6
        assert stats["metrics"]["ao.agents"] == 6
