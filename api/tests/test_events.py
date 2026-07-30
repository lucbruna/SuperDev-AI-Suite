from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.events import EventBus, EventDispatcher, EventStore, CallbackManager  # noqa: E402
from api.events.event_bus import Event, EventPriority  # noqa: E402


class TestEvent:
    def test_create_event(self) -> None:
        event = Event.create("user.created", {"id": "123"}, source="test")
        assert event.topic == "user.created"
        assert event.data == {"id": "123"}
        assert event.source == "test"
        assert event.priority == EventPriority.NORMAL
        assert event.id is not None

    def test_event_defaults(self) -> None:
        event = Event.create("test")
        assert event.data == {}


class TestEventBus:
    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self) -> None:
        bus = EventBus()
        received: list[Event] = []

        async def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe("test", handler)
        event = Event.create("test", {"msg": "hello"})
        await bus.publish(event)
        await bus.start(num_workers=1)
        await asyncio.sleep(0.1)
        await bus.stop()
        assert len(received) == 1
        assert received[0].data["msg"] == "hello"

    def test_wildcard_subscribe(self) -> None:
        bus = EventBus()
        received: list[Event] = []

        async def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe("*", handler)
        assert bus.subscriber_count == 1

    @pytest.mark.asyncio
    async def test_subscribe_once(self) -> None:
        bus = EventBus()
        received: list[Event] = []

        async def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe_once("test", handler)
        event = Event.create("test")
        await bus.publish(event)
        await bus.publish(event)
        await bus.start(num_workers=1)
        await asyncio.sleep(0.1)
        await bus.stop()
        assert len(received) == 1


import asyncio  # noqa: E402, F811


class TestEventStore:
    def test_append_and_retrieve(self) -> None:
        store = EventStore(max_events=100)
        event = Event.create("test", {"key": "value"})
        store.append(event)
        assert store.count() == 1
        retrieved = store.get_by_id(event.id)
        assert retrieved is not None
        assert retrieved.data["key"] == "value"

    def test_search_by_topic(self) -> None:
        store = EventStore()
        store.append(Event.create("a", {"v": 1}))
        store.append(Event.create("b", {"v": 2}))
        store.append(Event.create("a", {"v": 3}))
        results = store.get_by_topic("a")
        assert len(results) == 2

    def test_max_events(self) -> None:
        store = EventStore(max_events=3)
        for i in range(5):
            store.append(Event.create("t", {"i": i}))
        assert store.count() == 3
        # Most recent events survive
        events = store.get_all()
        assert events[-1].data["i"] == 4

    def test_since(self) -> None:
        import time
        store = EventStore()
        t0 = time.time()
        store.append(Event.create("a"))
        t1 = time.time()
        store.append(Event.create("b"))
        results = store.since(t1)
        assert len(results) == 1
        assert results[0].topic == "b"


class TestEventDispatcher:
    def test_initialization(self) -> None:
        bus = EventBus()
        dispatcher = EventDispatcher(bus)
        assert dispatcher is not None


class TestCallbackManager:
    def test_register_callback(self) -> None:
        bus = EventBus()
        mgr = CallbackManager(bus)
        async def handler(**kwargs: Any) -> str:
            return "done"
        cb_id = mgr.register("test.event", handler)
        assert cb_id is not None
        callbacks = mgr.get_callbacks("test.event")
        assert len(callbacks) == 1

    def test_unregister_callback(self) -> None:
        bus = EventBus()
        mgr = CallbackManager(bus)
        async def handler(**kwargs: Any) -> str:
            return "done"
        cb_id = mgr.register("test.event", handler)
        assert mgr.unregister(cb_id)
        assert not mgr.unregister("nonexistent")
