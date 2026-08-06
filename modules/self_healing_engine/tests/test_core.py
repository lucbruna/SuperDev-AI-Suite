"""Tests for the core foundations: context, events, state, memory, registry."""
from __future__ import annotations

from modules.self_healing_engine.core import (
    HealingContext,
    HealingEventBus,
    HealingMemory,
    HealingRegistry,
    HealingRegistryError,
    HealingState,
)
from modules.self_healing_engine.tests.helpers import make_context


def test_event_bus_publish_history_and_subscribe() -> None:
    bus = HealingEventBus()
    seen: list[str] = []

    def on_event(event) -> None:
        seen.append(event.type)

    bus.subscribe("health.changed", on_event)
    bus.publish("health.changed", {"status": "healthy"})
    bus.publish("other", {})

    assert bus.last_sequence == 2
    assert len(bus.history()) == 2
    assert len(bus.history_of("health.changed")) == 1
    assert seen == ["health.changed"]


def test_state_dirty_tracking_and_helpers() -> None:
    state = HealingState()
    state.set_health_score(85.0)
    state.set_health_status("degraded")
    state.open_incident()

    assert state.last_health_score == 85.0
    assert state.health_status == "degraded"
    assert state.active_incidents == 1
    assert "health_score" in state.dirty_keys()

    state.mark_clean()
    assert state.dirty_keys() == set()


def test_memory_round_trip_and_lru() -> None:
    memory = HealingMemory(max_entries=2)
    memory.remember("a", 1)
    memory.remember("b", 2)
    memory.remember("c", 3)  # evicts "a"

    assert not memory.has("a")
    assert memory.recall("b") == 2
    assert memory.recall("c") == 3
    assert len(memory) == 2


def test_memory_json_persistence(tmp_path) -> None:
    memory = HealingMemory()
    memory.remember("k", {"v": 1})
    path = tmp_path / "mem.json"
    memory.save(path)

    loaded = HealingMemory.load(path)
    assert loaded.recall("k") == {"v": 1}

    missing = HealingMemory.load(tmp_path / "nope.json")
    assert len(missing) == 0


def test_registry_register_get_and_errors() -> None:
    registry = HealingRegistry()

    def component() -> None:
        return None

    registry.register("c", component)
    assert registry.has("c")
    assert registry.names() == ["c"]
    assert registry.get("c") is component

    try:
        registry.register("c", component)
    except HealingRegistryError:
        pass
    else:
        raise AssertionError("duplicate registration should raise")

    try:
        registry.get("missing")
    except HealingRegistryError:
        pass
    else:
        raise AssertionError("missing component should raise")

    registry.unregister("c")
    assert len(registry) == 0


def test_context_publish_record_increment_artifacts() -> None:
    ctx = make_context()
    ctx.publish("cycle.completed", {"status": "ok"})
    ctx.record("cycles", 1)
    ctx.increment("cycles")
    ctx.set_artifact("plan", {"kind": "dependency"})

    summary = ctx.summary()
    assert summary["stats"]["cycles"] == 2
    assert summary["events"] == 1
    assert summary["artifacts"] == ["plan"]
    assert ctx.get_artifact("plan") == {"kind": "dependency"}
