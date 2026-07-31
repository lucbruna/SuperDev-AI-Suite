"""Tests for the Agent Orchestration core (Volume 31, Fase 1)."""

from __future__ import annotations

import pytest

from agent_orchestration import (build_orchestrator, coerce_bool,
                                 coerce_number, new_id, normalize, safe_get,
                                 tokenize, top_n)
from agent_orchestration.orchestrator_config import OrchestratorConfig
from agent_orchestration.orchestrator_events import (OrchestratorEventType,
                                                     OrchestratorEvents)
from agent_orchestration.orchestrator_models import (AgentCapability,
                                                     AgentProfile,
                                                     AgentStatus, AgentTask,
                                                     MessageType, Priority,
                                                     RiskLevel, TaskStatus)
from agent_orchestration.orchestrator_protocols import now
from agent_orchestration.orchestrator_registry import OrchestratorRegistry
from agent_orchestration.orchestrator_security import OrchestratorSecurity


class TestConfig:
    def test_defaults_and_get(self):
        config = OrchestratorConfig()
        assert config.max_agents == 50
        assert config.get("max_retries") == 2
        assert config.get("missing", 7) == 7

    def test_overrides_and_snapshot(self):
        config = OrchestratorConfig(max_agents=10, custom_opt="x")
        assert config.max_agents == 10
        snapshot = config.snapshot()
        assert snapshot["max_agents"] == 10
        assert "custom_opt" not in snapshot

    def test_merge(self):
        config = OrchestratorConfig().merge({"max_agents": 99})
        assert config.max_agents == 99


class TestEvents:
    def test_on_publish_off(self):
        events = OrchestratorEvents()
        seen = []
        handler = lambda payload: seen.append(payload)  # noqa: E731
        events.on(OrchestratorEventType.TASK_COMPLETED, handler)
        events.publish(OrchestratorEventType.TASK_COMPLETED,
                       {"task_id": "t1"})
        events.off(OrchestratorEventType.TASK_COMPLETED, handler)
        events.publish(OrchestratorEventType.TASK_COMPLETED,
                       {"task_id": "t2"})
        assert len(seen) == 1

    def test_once(self):
        events = OrchestratorEvents()
        seen = []
        events.once(OrchestratorEventType.MESSAGE_SENT,
                    lambda payload: seen.append(payload))
        events.publish(OrchestratorEventType.MESSAGE_SENT, {})
        events.publish(OrchestratorEventType.MESSAGE_SENT, {})
        assert len(seen) == 1

    def test_listener_isolation(self):
        events = OrchestratorEvents()

        def boom(_payload):
            raise ValueError("boom")

        events.on(OrchestratorEventType.TASK_FAILED, boom)
        events.publish(OrchestratorEventType.TASK_FAILED, {})  # no raise


class TestProtocols:
    def test_new_id_prefix(self):
        assert new_id("task").startswith("task-")
        assert new_id("agent").startswith("agent-")

    def test_coerce(self):
        assert coerce_bool("true") is True
        assert coerce_bool("nope") is False
        assert coerce_number("3.5") == 3.5
        assert coerce_number("abc", 1.0) == 1.0

    def test_text_helpers(self):
        assert normalize("  Olá   Mundo ") == "olá mundo"
        assert tokenize("criar app financeiro") == [
            "criar", "app", "financeiro"]

    def test_safe_get(self):
        data = {"a": {"b": 1}}
        assert safe_get(data, "a.b") == 1
        assert safe_get(data, "a.c", 9) == 9

    def test_top_n(self):
        items = [{"v": 1}, {"v": 5}, {"v": 3}]
        result = top_n(items, key=lambda item: item["v"], limit=2)
        assert [item["v"] for item in result] == [5, 3]


class TestModels:
    def test_agent_profile(self):
        agent = AgentProfile(
            agent_id="agent-1", name="Coding AI",
            capabilities=[AgentCapability(name="code",
                                          tools=["editor", "git"])],
            permissions=["write.project"])
        assert agent.has_capability("code")
        assert agent.can("write.project")
        assert not agent.can("delete.prod")

    def test_priority_rank(self):
        assert Priority.CRITICAL.rank > Priority.LOW.rank

    def test_task_defaults(self):
        task = AgentTask(task_id="task-1", title="t")
        assert task.status == TaskStatus.PENDING
        assert task.risk_level == RiskLevel.LOW
        assert task.priority == Priority.MEDIUM


class TestSecurity:
    def test_permissions(self):
        security = OrchestratorSecurity()
        assert security.can("a1", "read", granted=["read", "write"])
        assert not security.can("a1", "delete")
        security.grant("a1", "delete")
        assert security.can("a1", "delete")

    def test_risk_approval(self):
        security = OrchestratorSecurity()
        assert security.requires_approval(RiskLevel.CRITICAL)
        assert not security.requires_approval(RiskLevel.LOW)
        assert not security.requires_approval(RiskLevel.CRITICAL, False)

    def test_approve_roles(self):
        security = OrchestratorSecurity()
        assert security.approve("admin")
        assert not security.approve("guest")

    def test_sanitize(self):
        security = OrchestratorSecurity()
        assert "<script>" not in security.sanitize("<script>alert(1)</script>")
        assert not security.is_safe("<script>alert(1)</script>")


class TestRegistry:
    def test_agent_crud(self):
        registry = OrchestratorRegistry()
        agent = AgentProfile(agent_id="a1", name="x")
        registry.register_agent(agent)
        assert registry.get_agent("a1") is agent
        assert registry.count_agents() == 1
        assert registry.remove_agent("a1")
        assert not registry.remove_agent("a1")

    def test_stats(self):
        registry = OrchestratorRegistry()
        registry.register_agent(AgentProfile(agent_id="a1", name="x"))
        registry.register_task(AgentTask(task_id="t1", title="t"))
        stats = registry.stats()
        assert stats["agents"] == 1
        assert stats["tasks"] == 1


class TestManagerAndEngine:
    @pytest.fixture
    def engine(self):
        return build_orchestrator()

    def test_agent_lifecycle(self, engine):
        agent = engine.register_agent("Coding AI", "criar código",
                                      role="developer")
        assert agent.agent_id.startswith("agent-")
        assert engine.get_agent(agent.agent_id) is agent
        assert len(engine.list_agents()) == 1
        assert engine.remove_agent(agent.agent_id)
        assert len(engine.list_agents()) == 0

    def test_task_flow(self, engine):
        task = engine.create_task("Criar API", priority=Priority.HIGH)
        assert task.status == TaskStatus.PENDING
        assert engine.update_task_status(task.task_id, TaskStatus.QUEUED)
        assert task.status == TaskStatus.QUEUED
        assert engine.update_task_status(task.task_id, TaskStatus.COMPLETED)
        assert task.completed_at > 0

    def test_agent_status_event(self, engine):
        agent = engine.register_agent("Planner AI")
        fired = []
        engine.events.on(OrchestratorEventType.AGENT_STATUS_CHANGED,
                         lambda payload: fired.append(payload))
        engine.manager.set_agent_status(agent.agent_id, AgentStatus.BUSY)
        assert len(fired) == 1
        assert fired[0]["status"] == "busy"

    def test_message_relay(self, engine):
        message = engine.manager.send_message(
            "agent-a", "agent-b", "preciso do schema",
            MessageType.REQUEST, {"db": "pg"})
        assert message.message_id.startswith("message-")
        assert engine.manager.list_messages()[0].content == "preciso do schema"

    def test_approval_flow(self, engine):
        task = engine.create_task("mudar produção",
                                  risk_level=RiskLevel.CRITICAL)
        assert engine.manager.require_approval(task.task_id, "risco alto")
        assert task.status == TaskStatus.APPROVAL_REQUIRED
        assert not engine.manager.resolve_approval(task.task_id, "guest", True)
        assert engine.manager.resolve_approval(task.task_id, "admin", True)
        assert task.status == TaskStatus.QUEUED

    def test_attach_subsystem(self, engine):
        fake = object()
        engine.attach_subsystem("planner_engine", fake)
        assert engine.planner_engine is fake
        assert engine.manager.planner_engine is fake
        assert "planner_engine" in engine.stats()["subsystems"]

    def test_runtime_lifecycle(self, engine):
        assert engine.start()
        assert not engine.start()
        assert engine.runtime.is_running()
        assert engine.stop()
        assert not engine.stop()

    def test_factory_overrides(self):
        engine = build_orchestrator({"max_agents": 3})
        assert engine.config.max_agents == 3

    def test_stats(self, engine):
        stats = engine.stats()
        assert "manager" in stats
        assert stats["runtime"]["state"] == "stopped"


class TestContext:
    def test_snapshot(self):
        from agent_orchestration.orchestrator_context import (
            OrchestratorContext)
        context = OrchestratorContext(project="ERP", owner="tom")
        context.set("branch", "main")
        snapshot = context.snapshot()
        assert snapshot["project"] == "ERP"
        assert snapshot["metadata"]["branch"] == "main"
        assert context.get("branch") == "main"
        assert context.get("missing", 0) == 0


class TestInterfaces:
    def test_abstract_binding(self):
        from agent_orchestration.orchestrator_interfaces import (
            AgentMemoryStore, CommunicationBus, DecisionEngine, Evaluator,
            LearningStore, PlannerStrategy, TaskExecutor, TaskScheduler)
        interfaces = [PlannerStrategy, TaskExecutor, CommunicationBus,
                      AgentMemoryStore, DecisionEngine, Evaluator,
                      TaskScheduler, LearningStore]
        assert all(getattr(interface, "__abstractmethods__")
                   for interface in interfaces)
