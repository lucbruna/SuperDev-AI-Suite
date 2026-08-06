"""Unit tests for the Digital Twin core package."""
from __future__ import annotations

import pytest

from modules.digital_twin.config.digital_twin_config import DigitalTwinConfig
from modules.digital_twin.core import (
    DigitalTwinContext,
    DigitalTwinEngine,
    DigitalTwinKernel,
    DigitalTwinManager,
    DigitalTwinPipeline,
    DigitalTwinRuntime,
    TwinEvent,
    TwinEventBus,
    TwinMemory,
    TwinRegistry,
    TwinRegistryError,
    TwinState,
)


def _echo_component(name: str):
    """Build a deterministic pipeline component recording its phase."""

    def run(ctx: DigitalTwinContext):
        ctx.record(f"ran.{name}", True)
        return {"component": name}

    return run


def _failing_component(ctx: DigitalTwinContext):
    raise RuntimeError("boom")


class TestTwinEventBus:
    def test_publish_assigns_sequence(self) -> None:
        bus = TwinEventBus()
        first = bus.publish("a", {"n": 1})
        second = bus.publish("a", {"n": 2})
        assert first.sequence == 1
        assert second.sequence == 2
        assert bus.last_sequence == 2

    def test_subscriber_receives_events(self) -> None:
        bus = TwinEventBus()
        seen: list[TwinEvent] = []
        bus.subscribe("cycle", seen.append)
        bus.publish("cycle", {"cycle": 3})
        assert len(seen) == 1
        assert seen[0].payload == {"cycle": 3}

    def test_subscriber_scoped_by_type(self) -> None:
        bus = TwinEventBus()
        seen: list[str] = []
        bus.subscribe("a", lambda e: seen.append(e.type))
        bus.publish("b", {})
        assert seen == []

    def test_history_and_clear(self) -> None:
        bus = TwinEventBus()
        bus.publish("a", {})
        bus.publish("b", {})
        bus.publish("a", {})
        assert len(bus.history()) == 3
        assert len(bus.history_of("a")) == 2
        bus.clear()
        assert bus.history() == []
        assert bus.last_sequence == 0

    def test_event_to_dict(self) -> None:
        event = TwinEvent(type="t", payload={"k": "v"}, sequence=9)
        d = event.to_dict()
        assert d["type"] == "t"
        assert d["payload"] == {"k": "v"}
        assert d["sequence"] == 9


class TestTwinRegistry:
    def test_register_get_has(self) -> None:
        reg = TwinRegistry()
        fn = lambda ctx: None  # noqa: E731
        reg.register("sync", fn)
        assert reg.has("sync")
        assert reg.get("sync") is fn
        assert reg.names() == ["sync"]

    def test_duplicate_raises_unless_overwrite(self) -> None:
        reg = TwinRegistry()
        reg.register("a", lambda ctx: None)
        with pytest.raises(TwinRegistryError):
            reg.register("a", lambda ctx: None)
        reg.register("a", lambda ctx: None, overwrite=True)
        assert len(reg) == 1

    def test_missing_raises(self) -> None:
        reg = TwinRegistry()
        with pytest.raises(TwinRegistryError):
            reg.get("nope")

    def test_unregister_and_clear(self) -> None:
        reg = TwinRegistry()
        reg.register("a", lambda ctx: None)
        reg.register("b", lambda ctx: None)
        reg.unregister("a")
        assert not reg.has("a")
        reg.clear()
        assert len(reg) == 0


class TestTwinState:
    def test_set_get_delete(self) -> None:
        state = TwinState()
        state.set("twin_status", "synced")
        assert state.get("twin_status") == "synced"
        assert state.get("missing", "d") == "d"
        state.delete("twin_status")
        assert not state.has("twin_status")

    def test_dirty_tracking(self) -> None:
        state = TwinState()
        state.set("a", 1)
        state.set("b", 2)
        assert state.dirty_keys() == {"a", "b"}
        state.mark_clean("a")
        assert state.dirty_keys() == {"b"}
        state.mark_clean()
        assert state.dirty_keys() == set()

    def test_status_helpers(self) -> None:
        state = TwinState()
        assert state.twin_status == "synced"
        state.mark_out_of_sync()
        assert state.twin_status == "out_of_sync"

    def test_to_from_dict(self) -> None:
        state = TwinState()
        state.set("a", 1)
        data = state.to_dict()
        other = TwinState()
        other.from_dict(data)
        assert other.get("a") == 1
        assert other.dirty_keys() == set()


class TestDigitalTwinContext:
    def test_record_increment_and_summary(self) -> None:
        ctx = DigitalTwinContext()
        ctx.record("a", 1)
        ctx.increment("a", 2)
        ctx.increment("b")
        assert ctx.stats["a"] == 3
        assert ctx.stats["b"] == 1
        summary = ctx.summary()
        assert summary["stats"]["a"] == 3

    def test_artifacts(self) -> None:
        ctx = DigitalTwinContext()
        ctx.set_artifact("plan", {"x": 1})
        assert ctx.get_artifact("plan") == {"x": 1}
        assert ctx.get_artifact("nope", "d") == "d"
        assert "plan" in ctx.summary()["artifacts"]

    def test_publish(self) -> None:
        ctx = DigitalTwinContext()
        ctx.publish("test.event", {"ok": True})
        assert len(ctx.events.history()) == 1

    def test_fresh_instances_are_independent(self) -> None:
        first = DigitalTwinContext()
        second = DigitalTwinContext()
        first.record("x", 1)
        assert second.stats == {}
        assert second.registry.names() == []


class TestDigitalTwinPipeline:
    def test_runs_registered_phases_in_order(self) -> None:
        ctx = DigitalTwinContext()
        for phase in ("sync", "simulate", "predict"):
            ctx.registry.register(phase, _echo_component(phase))
        pipeline = DigitalTwinPipeline()
        result = pipeline.run(ctx)
        assert result.status() == "ran"
        assert result.phases_run() == ["sync", "simulate", "predict"]
        assert ctx.get_artifact("sync") == {"component": "sync"}

    def test_skips_unregistered_phases(self) -> None:
        ctx = DigitalTwinContext()
        pipeline = DigitalTwinPipeline()
        result = pipeline.run(ctx)
        assert result.status() == "empty"
        assert all(s.status == "skipped" for s in result.steps)
        assert len(result.steps) == len(pipeline.phases)

    def test_disabled_phases_skipped(self) -> None:
        ctx = DigitalTwinContext()
        ctx.registry.register("sync", _echo_component("sync"))
        ctx.config.simulation.enabled = False
        ctx.registry.register("simulate", _echo_component("simulate"))
        result = DigitalTwinPipeline().run(ctx)
        statuses = {s.phase: s.status for s in result.steps}
        assert statuses["sync"] == "ran"
        assert statuses["simulate"] == "skipped"

    def test_failing_component_is_isolated(self) -> None:
        ctx = DigitalTwinContext()
        ctx.registry.register("sync", _failing_component)
        ctx.registry.register("predict", _echo_component("predict"))
        result = DigitalTwinPipeline().run(ctx)
        assert result.status() == "failed"
        by_phase = {s.phase: s.status for s in result.steps}
        assert by_phase["sync"] == "failed"
        assert by_phase["predict"] == "ran"
        assert "pipeline.sync.error" in ctx.stats


class TestDigitalTwinEngine:
    def test_run_publishes_cycle_event(self) -> None:
        ctx = DigitalTwinContext()
        ctx.registry.register("sync", _echo_component("sync"))
        engine = DigitalTwinEngine()
        result = engine.run(ctx)
        assert result.cycle == 1
        assert engine.cycles == 1
        events = ctx.events.history_of("cycle.completed")
        assert len(events) == 1
        assert events[0].payload["status"] == "ran"
        assert ctx.stats["engine.cycles"] == 1

    def test_cycles_increment(self) -> None:
        ctx = DigitalTwinContext()
        engine = DigitalTwinEngine()
        engine.run(ctx)
        engine.run(ctx)
        assert engine.cycles == 2


class TestDigitalTwinKernel:
    def test_tick_runs_cycle_at_interval(self) -> None:
        config = DigitalTwinConfig()
        config.sync.interval_seconds = 3
        ctx = DigitalTwinContext(config=config)
        ctx.registry.register("sync", _echo_component("sync"))
        kernel = DigitalTwinKernel(ctx, interval_seconds=3)
        assert kernel.tick(2) == 0
        assert kernel.ticks == 2
        assert kernel.tick(1) == 1
        assert kernel.ticks == 3
        assert kernel.status().cycles == 1

    def test_tick_without_components_still_counts(self) -> None:
        ctx = DigitalTwinContext()
        kernel = DigitalTwinKernel(ctx, interval_seconds=1)
        assert kernel.tick(2) == 2
        assert kernel.status().cycles == 2

    def test_status_fields(self) -> None:
        ctx = DigitalTwinContext()
        kernel = DigitalTwinKernel(ctx, interval_seconds=5)
        kernel.start()
        kernel.tick(1)
        status = kernel.status()
        assert status.running is True
        assert status.ticks == 1
        assert status.next_cycle_in_ticks == 4

    def test_interval_clamped_to_min_one(self) -> None:
        ctx = DigitalTwinContext()
        kernel = DigitalTwinKernel(ctx, interval_seconds=0)
        assert kernel.status().interval_seconds == 1


class TestTwinMemory:
    def test_remember_recall_forget(self) -> None:
        memory = TwinMemory()
        memory.remember("last_sync", "ok")
        assert memory.recall("last_sync") == "ok"
        assert memory.has("last_sync")
        assert memory.forget("last_sync") is True
        assert not memory.has("last_sync")
        assert memory.forget("last_sync") is False

    def test_max_entries_evicts_oldest(self) -> None:
        memory = TwinMemory(max_entries=2)
        memory.remember("a", 1)
        memory.remember("b", 2)
        memory.remember("c", 3)
        assert memory.keys() == ["b", "c"]

    def test_recall_refreshes_recency(self) -> None:
        memory = TwinMemory(max_entries=2)
        memory.remember("a", 1)
        memory.remember("b", 2)
        memory.recall("a")
        memory.remember("c", 3)
        assert memory.keys() == ["a", "c"]

    def test_save_and_load_roundtrip(self, tmp_path) -> None:
        path = tmp_path / "mem.json"
        memory = TwinMemory()
        memory.remember("k", {"v": [1, 2]})
        memory.save(str(path))
        loaded = TwinMemory.load(str(path))
        assert loaded.recall("k") == {"v": [1, 2]}

    def test_load_missing_file_returns_empty(self, tmp_path) -> None:
        loaded = TwinMemory.load(str(tmp_path / "missing.json"))
        assert len(loaded) == 0

    def test_load_corrupt_raises(self, tmp_path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(Exception):
            TwinMemory.load(str(path))


class TestDigitalTwinManager:
    def test_start_stop_events(self) -> None:
        manager = DigitalTwinManager()
        manager.start()
        assert manager.state().running is True
        manager.stop()
        assert manager.state().running is False
        types = [e.type for e in manager.context.events.history()]
        assert "twin.started" in types
        assert "twin.stopped" in types

    def test_run_cycle_marks_synced(self) -> None:
        manager = DigitalTwinManager()
        manager.start()
        manager.run_cycle()
        assert manager.state().twin_status == "synced"
        assert manager.state().cycles == 1

    def test_register_component(self) -> None:
        manager = DigitalTwinManager()
        manager.register_component("sync", _echo_component("sync"))
        assert manager.context.registry.has("sync")


class TestDigitalTwinRuntime:
    def test_facade_wiring(self) -> None:
        runtime = DigitalTwinRuntime()
        assert isinstance(runtime.context, DigitalTwinContext)
        assert isinstance(runtime.registry, TwinRegistry)
        assert runtime.engine.cycles == 0

    def test_run_cycle_via_manager(self) -> None:
        runtime = DigitalTwinRuntime()
        runtime.register_component("sync", _echo_component("sync"))
        result = runtime.run_cycle()
        assert result.cycle == 1

    def test_kernel_tick_via_manager(self) -> None:
        runtime = DigitalTwinRuntime()
        runtime.config.sync.interval_seconds = 1
        runtime.register_component("sync", _echo_component("sync"))
        assert runtime.tick(2) == 2
        assert runtime.kernel_status().cycles == 2
