"""Tests for middleware module: rate_limit (CircuitBreaker) and events module."""

import pytest
import time
from backend.middleware.rate_limit import CircuitBreaker
from backend.events.event_bus import Event, EventBus
from backend.events.event_registry import EventRegistry


# ── CircuitBreaker ──────────────────────────────────────────────────


class TestCircuitBreaker:
    def test_initial_state(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)
        assert cb.state == "closed"
        assert cb.failure_count == 0
        assert cb.is_available() is True

    def test_successful_call(self):
        cb = CircuitBreaker(failure_threshold=3)
        result = cb.call(lambda: "ok")
        assert result == "ok"
        assert cb.state == "closed"
        assert cb.failure_count == 0

    def test_failure_increments_count(self):
        cb = CircuitBreaker(failure_threshold=3)
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        assert cb.failure_count == 1
        assert cb.state == "closed"

    def test_open_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2)
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        assert cb.state == "open"
        assert cb.is_available() is False

    def test_open_raises_immediately(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=10.0)
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        # Circuit is now open, should raise without calling func
        with pytest.raises(Exception, match="Circuit breaker is open"):
            cb.call(lambda: "should not run")

    def test_half_open_after_recovery(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        assert cb.state == "open"
        time.sleep(0.15)
        # Should transition to half-open and allow call
        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.state == "closed"

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=2)
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        assert cb.state == "open"
        cb.reset()
        assert cb.state == "closed"
        assert cb.failure_count == 0
        assert cb.is_available() is True

    @pytest.mark.asyncio
    async def test_call_async_success(self):
        cb = CircuitBreaker(failure_threshold=3)

        async def func():
            return "async_ok"

        result = await cb.call_async(func)
        assert result == "async_ok"
        assert cb.state == "closed"

    @pytest.mark.asyncio
    async def test_call_async_failure(self):
        cb = CircuitBreaker(failure_threshold=2)

        async def func():
            raise ValueError("async fail")

        with pytest.raises(ValueError):
            await cb.call_async(func)
        assert cb.failure_count == 1

    @pytest.mark.asyncio
    async def test_call_async_open_raises(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=10.0)

        async def func():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            await cb.call_async(func)
        assert cb.state == "open"
        with pytest.raises(Exception, match="Circuit breaker is open"):
            await cb.call_async(lambda: None)


# ── EventBus ────────────────────────────────────────────────────────


class TestEvent:
    def test_creation(self):
        event = Event(id="e1", type="user.created", data={"user_id": "123"})
        assert event.type == "user.created"
        assert event.data["user_id"] == "123"
        assert event.source == ""
        assert event.timestamp is not None


class TestEventBus:
    @pytest.mark.asyncio
    async def test_publish_event(self):
        bus = EventBus()
        event = await bus.publish("user.created", {"user_id": "123"})
        assert event.type == "user.created"
        assert event.data["user_id"] == "123"
        assert len(bus.get_history()) == 1

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe("user.created", handler)
        await bus.publish("user.created", {"user_id": "123"})
        assert len(received) == 1
        assert received[0].data["user_id"] == "123"

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe("user.created", handler)
        bus.unsubscribe("user.created", handler)
        await bus.publish("user.created")
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_publish_no_handlers(self):
        bus = EventBus()
        event = await bus.publish("user.created")
        assert event.type == "user.created"

    @pytest.mark.asyncio
    async def test_publish_handler_error_ignored(self):
        bus = EventBus()

        async def bad_handler(event):
            raise RuntimeError("oops")

        bus.subscribe("user.created", bad_handler)
        # Should not raise
        event = await bus.publish("user.created")
        assert event is not None

    def test_get_history(self):
        bus = EventBus()
        # Manually add events to history
        bus._history.append(Event(id="1", type="user.created"))
        bus._history.append(Event(id="2", type="user.updated"))
        bus._history.append(Event(id="3", type="user.created"))

        all_events = bus.get_history()
        assert len(all_events) == 3

        created = bus.get_history(event_type="user.created")
        assert len(created) == 2

    def test_get_history_limit(self):
        bus = EventBus()
        for i in range(10):
            bus._history.append(Event(id=str(i), type="test"))
        limited = bus.get_history(limit=3)
        assert len(limited) == 3


# ── EventRegistry ───────────────────────────────────────────────────


class TestEventRegistry:
    def test_get_registered_event(self):
        desc = EventRegistry.get("user.created")
        assert desc == "User account created"

    def test_get_unregistered_event(self):
        assert EventRegistry.get("nonexistent") is None

    def test_list_events(self):
        events = EventRegistry.list_events()
        assert "user.created" in events
        assert "project.created" in events
        assert len(events) >= 14

    def test_register_new_event(self):
        EventRegistry.register("custom.event", "A custom event")
        assert EventRegistry.get("custom.event") == "A custom event"
