"""Unit tests: monitoring, memory, database, websocket, scheduler, utils."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_events import EvolutionEvent
from modules.ai_evolution_engine.database.database_adapter import DatabaseAdapter
from modules.ai_evolution_engine.memory.memory_manager import MemoryManager
from modules.ai_evolution_engine.monitoring.monitoring_engine import (
    MonitoringEngine,
)
from modules.ai_evolution_engine.scheduler.scheduler_engine import (
    ScheduledJob,
    SchedulerEngine,
)
from modules.ai_evolution_engine.tests.helpers import make_context
from modules.ai_evolution_engine.utils.deterministic import (
    clamp,
    pct,
    stable_hash,
)
from modules.ai_evolution_engine.websocket.event_hub import EventHub, WSEventMessage


def test_monitoring_reports_healthy():
    ctx = make_context(
        cache_hit_ratio=0.95,
        test_pass_rate=1.0,
        resource_usage_ratio=0.4,
    )
    snapshot = MonitoringEngine().collect(ctx)
    assert snapshot.healthy is True
    assert snapshot.issues == []


def test_monitoring_reports_issues_and_history():
    engine = MonitoringEngine()
    ctx = make_context(
        cache_hit_ratio=0.5,
        test_pass_rate=0.5,
        resource_usage_ratio=0.95,
    )
    snapshot = engine.collect(ctx)
    assert snapshot.healthy is False
    assert len(snapshot.issues) == 3
    assert len(engine.history()) == 1


def test_memory_manager_namespacing():
    memory = MemoryManager()
    memory.store("key", {"v": 1}, namespace="alpha")
    memory.store("key", {"v": 2}, namespace="beta")
    assert memory.load("key", namespace="alpha") == {"v": 1}
    assert memory.load("key", namespace="beta") == {"v": 2}
    assert memory.snapshot("alpha") == {"key": {"v": 1}}
    memory.clear_namespace("alpha")
    assert memory.snapshot("alpha") == {}


def test_database_adapter_crud():
    db = DatabaseAdapter()
    db.insert("items", "a", {"name": "A"})
    db.insert("items", "b", {"name": "B"})
    assert db.get("items", "a") == {"name": "A"}
    assert len(db.list("items")) == 2
    db.delete("items", "a")
    assert db.get("items", "a") is None
    assert db.snapshot() == {"items": {"b": {"name": "B"}}}


def test_event_hub_publish_and_subscribe():
    hub = EventHub()
    received: list[str] = []

    def handler(message: WSEventMessage) -> None:
        received.append(message.channel)

    hub.subscribe("evolution", handler)
    hub.publish(WSEventMessage(channel="evolution", payload={"x": 1}))
    assert received == ["evolution"]
    hub.unsubscribe("evolution", handler)
    hub.publish(WSEventMessage(channel="evolution", payload={"x": 2}))
    assert received == ["evolution"]


def test_event_hub_publishes_evolution_events():
    hub = EventHub()
    messages: list[dict] = []
    hub.subscribe(
        "evolution",
        lambda m: messages.append(m.to_dict()),
    )
    hub.publish_event(EvolutionEvent("evolution.tick", {"tick": 1}))
    assert messages[0]["channel"] == "evolution"
    assert messages[0]["payload"]["event"]["type"] == "evolution.tick"


def test_scheduler_ticks_periodically():
    scheduler = SchedulerEngine()
    runs: list[int] = []
    scheduler.register(
        ScheduledJob(name="job", interval=2, fn=lambda: runs.append(1))
    )
    scheduler.tick()  # not ready yet (remaining=2)
    assert runs == []
    scheduler.tick()
    assert runs == [1]
    assert scheduler.names() == ["job"]


def test_scheduler_unregister():
    scheduler = SchedulerEngine()
    scheduler.register(ScheduledJob(name="job", interval=1, fn=lambda: None))
    scheduler.unregister("job")
    assert scheduler.names() == []


def test_utils_deterministic():
    assert stable_hash("a", 1) == stable_hash("a", 1)
    assert stable_hash("a", 1) != stable_hash("a", 2)
    assert clamp(1.5) == 1.0
    assert clamp(-1) == 0.0
    assert pct(0.5) == 50.0
