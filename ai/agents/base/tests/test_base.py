from __future__ import annotations

from ..base_agent import BaseAgent
from ..abstract_agent import AbstractAgent
from ..autonomous_agent import AutonomousAgent
from ..reactive_agent import ReactiveAgent
from ..proactive_agent import ProactiveAgent
from ..cognitive_agent import CognitiveAgent
from ..intelligent_agent import IntelligentAgent
from ..agent_context import AgentContext
from ..agent_memory import AgentMemory
from ..agent_identity import AgentIdentity
from ..agent_profile import AgentProfile
from ..agent_capabilities import AgentCapabilities
from ..agent_permissions import AgentPermissions
from ..agent_state import AgentState, AgentStateManager
from ..agent_config import AgentConfig
from ..heartbeat import Heartbeat
from ..lifecycle import Lifecycle, LifecycleStage


class TestBaseAgent:
    def test_create(self) -> None:
        a = BaseAgent("a1")
        assert a.agent_id == "a1"
        assert a.status == "idle"

    def test_execute(self) -> None:
        a = BaseAgent("a1")
        r = a.execute({"type": "test"})
        assert r["status"] == "completed"

    def test_to_dict(self) -> None:
        a = BaseAgent("a1", "TestAgent")
        d = a.to_dict()
        assert d["name"] == "TestAgent"


class TestAbstractAgent:
    def test_abstract(self) -> None:
        assert issubclass(BaseAgent, AbstractAgent) is False
        assert hasattr(AbstractAgent, "execute")


class TestAutonomousAgent:
    def test_create(self) -> None:
        a = AutonomousAgent("a1")
        assert a.autonomy_level == 0.5

    def test_set_autonomy(self) -> None:
        a = AutonomousAgent("a1")
        a.set_autonomy(0.9)
        assert a.autonomy_level == 0.9

    def test_decide(self) -> None:
        a = AutonomousAgent("a1")
        a.set_autonomy(0.8)
        assert a.decide({}) == "execute"
        a.set_autonomy(0.5)
        assert a.decide({}) == "request_guidance"


class TestReactiveAgent:
    def test_react(self) -> None:
        a = ReactiveAgent("a1")
        a.register_stimulus("ping", "pong")
        assert a.react("ping") == "pong"

    def test_execute(self) -> None:
        a = ReactiveAgent("a1")
        a.register_stimulus("ping", "pong")
        r = a.execute({"stimulus": "ping"})
        assert r["response"] == "pong"


class TestProactiveAgent:
    def test_goals(self) -> None:
        a = ProactiveAgent("a1")
        a.add_goal("build")
        assert "build" in a.get_goals()

    def test_propose_actions(self) -> None:
        a = ProactiveAgent("a1")
        a.add_goal("build")
        actions = a.propose_actions()
        assert "work_on_build" in actions


class TestCognitiveAgent:
    def test_learn_recall(self) -> None:
        a = CognitiveAgent("a1")
        a.learn("x", 42)
        assert a.recall("x") == 42

    def test_reason(self) -> None:
        a = CognitiveAgent("a1")
        assert a.reason({"problem": "error"}) == "analyzing"
        assert a.reason({}) == "observing"


class TestIntelligentAgent:
    def test_analyze(self) -> None:
        a = IntelligentAgent("a1")
        r = a.analyze({"task": "test"})
        assert "decision" in r

    def test_inheritance(self) -> None:
        a = IntelligentAgent("a1")
        a.learn("x", 10)
        assert a.recall("x") == 10
        a.set_autonomy(0.9)
        assert a.autonomy_level == 0.9


class TestAgentContext:
    def test_set_get(self) -> None:
        ctx = AgentContext("a1")
        ctx.set("key", "value")
        assert ctx.get("key") == "value"

    def test_parent(self) -> None:
        ctx = AgentContext("a1")
        ctx.parent = "p1"
        assert ctx.parent == "p1"

    def test_clear(self) -> None:
        ctx = AgentContext("a1")
        ctx.set("k", "v")
        ctx.clear()
        assert ctx.get("k") is None


class TestAgentMemory:
    def test_remember_recall(self) -> None:
        m = AgentMemory()
        m.remember("key", "value")
        assert m.recall("key") == "value"

    def test_forget(self) -> None:
        m = AgentMemory()
        m.remember("k", "v")
        assert m.forget("k") is True
        assert m.recall("k") is None


class TestAgentIdentity:
    def test_create(self) -> None:
        i = AgentIdentity("a1", "worker")
        assert i.agent_id == "a1"
        assert i.agent_type == "worker"

    def test_version(self) -> None:
        i = AgentIdentity("a1", "worker")
        i.version = "2.0.0"
        assert i.version == "2.0.0"


class TestAgentProfile:
    def test_specialty(self) -> None:
        p = AgentProfile("a1", "backend")
        assert p.specialty == "backend"

    def test_skills(self) -> None:
        p = AgentProfile("a1")
        p.add_skill("python")
        assert p.has_skill("python")
        assert not p.has_skill("java")


class TestAgentCapabilities:
    def test_add_has(self) -> None:
        c = AgentCapabilities()
        c.add("code")
        assert c.has("code")

    def test_list_all(self) -> None:
        c = AgentCapabilities()
        c.add("a")
        c.add("b")
        assert len(c.list_all()) == 2


class TestAgentPermissions:
    def test_allow_can(self) -> None:
        p = AgentPermissions()
        p.allow("read")
        assert p.can("read")
        assert not p.can("write")

    def test_deny(self) -> None:
        p = AgentPermissions()
        p.allow("read")
        p.deny("read")
        assert not p.can("read")


class TestAgentStateManager:
    def test_transition(self) -> None:
        sm = AgentStateManager()
        assert sm.state == AgentState.CREATED
        assert sm.transition(AgentState.INITIALIZING) is True
        assert sm.state == AgentState.INITIALIZING

    def test_invalid_transition(self) -> None:
        sm = AgentStateManager()
        assert sm.transition(AgentState.STOPPED) is False


class TestAgentConfig:
    def test_get_set(self) -> None:
        c = AgentConfig("a1", {"timeout": 30})
        assert c.get("timeout") == 30
        c.set("retries", 3)
        assert c.get("retries") == 3

    def test_update(self) -> None:
        c = AgentConfig("a1")
        c.update({"timeout": 30})
        assert c.get("timeout") == 30


class TestHeartbeat:
    def test_beat(self) -> None:
        h = Heartbeat("a1")
        h.beat()
        assert h.beat_count == 1
        assert h.last_beat is not None

    def test_is_alive_no_beat(self) -> None:
        h = Heartbeat("a1")
        assert not h.is_alive()


class TestLifecycle:
    def test_transition(self) -> None:
        lc = Lifecycle()
        assert lc.stage == LifecycleStage.CREATED
        assert lc.transition(LifecycleStage.INITIALIZED) is True
        assert lc.stage == LifecycleStage.INITIALIZED

    def test_invalid(self) -> None:
        lc = Lifecycle()
        assert lc.transition(LifecycleStage.DESTROYED) is True
        assert lc.transition(LifecycleStage.STARTED) is False

    def test_is_active(self) -> None:
        lc = Lifecycle()
        assert not lc.is_active()
