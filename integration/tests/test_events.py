"""Tests for the events subsystem (events/)."""

from __future__ import annotations

from typing import Any

from integration.events.event_bus import EventBus
from integration.events.event_engine import EventEngine
from integration.events.queue import EventQueue
from integration.events.routing import EventRouter
from integration.events.scheduler import EventScheduler


class TestEventRouter:
    def test_exact_and_wildcard_routing(self) -> None:
        router = EventRouter()
        router.add_rule("order.created", "orders")
        router.add_rule("order.*", "order-svc")
        router.add_rule("*", "audit")
        assert router.route("order.created") == ["audit", "order-svc", "orders"]
        assert router.route("payment.received") == ["audit"]

    def test_clear_and_rules(self) -> None:
        router = EventRouter()
        router.add_rule("a", "b")
        assert len(router.rules()) == 1
        router.clear()
        assert router.rules() == []


class TestEventQueue:
    def test_enqueue_process(self) -> None:
        queue = EventQueue()
        seen: list[dict[str, Any]] = []
        queue.enqueue({"type": "a"}, lambda e: seen.append(e))
        queue.enqueue({"type": "b"}, lambda e: seen.append(e))
        assert queue.size() == 2
        assert queue.process(1) == 1
        assert queue.size() == 1
        assert queue.process() == 1
        assert [e["type"] for e in seen] == ["a", "b"]

    def test_clear(self) -> None:
        queue = EventQueue()
        queue.enqueue({"type": "a"}, lambda e: None)
        queue.clear()
        assert queue.size() == 0


class TestEventBus:
    def test_publish_and_process(self) -> None:
        bus = EventBus()
        bus.router.add_rule("*", "all")
        seen: list[dict[str, Any]] = []
        bus.subscribe("all", lambda e: seen.append(e))
        event_id = bus.publish("order.created", {"order_id": "1"})
        assert event_id
        assert len(bus.published()) == 1
        assert bus.process() == 1
        assert len(seen) == 1
        assert seen[0]["payload"] == {"order_id": "1"}

    def test_no_matching_subscriber(self) -> None:
        bus = EventBus()
        bus.router.add_rule("x", "target")
        bus.publish("x", {})
        # No subscriber registered for 'target' -> nothing queued.
        assert bus.process() == 0

    def test_subscriber_count(self) -> None:
        bus = EventBus()
        bus.subscribe("a", lambda e: None)
        bus.subscribe("a", lambda e: None)
        bus.subscribe("b", lambda e: None)
        assert bus.subscriber_count() == 3


class TestEventScheduler:
    def test_one_shot(self) -> None:
        bus = EventBus()
        bus.router.add_rule("*", "all")
        seen: list[dict[str, Any]] = []
        bus.subscribe("all", lambda e: seen.append(e))
        scheduler = EventScheduler(bus)
        scheduler.schedule("j1", "tick", {"n": 1}, delay=-1)  # immediately due
        assert scheduler.run_due() == 1
        assert bus.process() == 1  # scheduler enqueues onto the bus
        assert len(seen) == 1
        assert scheduler.run_due() == 0  # one-shot removed
        assert scheduler.cancel("j1") is False

    def test_recurring_and_cancel(self) -> None:
        bus = EventBus()
        scheduler = EventScheduler(bus)
        scheduler.schedule("j2", "tick", {}, delay=-1, interval=9999)
        assert scheduler.run_due() == 1
        assert scheduler.jobs()["j2"] == 1
        assert scheduler.cancel("j2") is True


class TestEventEngine:
    def test_emit_on_drain(self) -> None:
        engine = EventEngine()
        engine.route("*", "all")
        seen: list[dict[str, Any]] = []
        engine.on("all", lambda e: seen.append(e))
        event_id = engine.emit("user.created", {"id": 1})
        assert event_id
        assert engine.drain() == 1
        assert len(seen) == 1
        assert engine.stats()["published"] == 1
        assert engine.stats()["queued"] == 0
