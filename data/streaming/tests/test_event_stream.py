from __future__ import annotations

import pytest

from SuperDev.data.data_engine import DataEngine
from SuperDev.data.streaming.event_stream import EventStream, StreamManager


class TestEventStream:
    @pytest.mark.asyncio
    async def test_publish_and_offsets(self) -> None:
        stream = EventStream("sensor")
        first = await stream.publish({"v": 1})
        second = await stream.publish({"v": 2})
        assert first.event_id != second.event_id
        assert stream.last_offset() == 2
        assert stream.size() == 2

    @pytest.mark.asyncio
    async def test_publish_copies_payload(self) -> None:
        stream = EventStream("s")
        payload = {"v": 1}
        event = await stream.publish(payload)
        payload["v"] = 999  # mutate original
        assert event.payload["v"] == 1

    @pytest.mark.asyncio
    async def test_subscribe_sync_handler(self) -> None:
        stream = EventStream("s")
        received: list[dict] = []
        stream.subscribe(lambda e: received.append(e.payload))
        await stream.publish({"v": 42})
        assert received == [{"v": 42}]

    @pytest.mark.asyncio
    async def test_subscribe_async_handler(self) -> None:
        stream = EventStream("s")
        received: list[str] = []

        async def handler(event) -> None:
            received.append(event.event_id)

        stream.subscribe(handler)
        await stream.publish({"v": 1})
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe(self) -> None:
        stream = EventStream("s")
        received: list[dict] = []

        def handler(event) -> None:
            received.append(event.payload)

        stream.subscribe(handler)
        assert stream.subscriber_count() == 1
        assert stream.unsubscribe(handler) is True
        assert stream.unsubscribe(handler) is False
        await stream.publish({"v": 1})
        assert received == []

    @pytest.mark.asyncio
    async def test_read_from_offset(self) -> None:
        stream = EventStream("s")
        for i in range(5):
            await stream.publish({"v": i})
        # events published at offsets 1..5; offset=2 → offsets 3,4,5
        after_two = stream.read(offset=2)
        assert [e.payload["v"] for e in after_two] == [2, 3, 4]
        assert stream.read(offset=99) == []

    @pytest.mark.asyncio
    async def test_replay(self) -> None:
        stream = EventStream("s")
        for i in range(3):
            await stream.publish({"v": i})
        replayed = stream.replay()
        assert [e.payload["v"] for e in replayed] == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_buffer_eviction(self) -> None:
        stream = EventStream("s", buffer_size=3)
        for i in range(10):
            await stream.publish({"v": i})
        assert stream.size() == 3
        assert stream.last_offset() == 10  # offsets keep counting

    @pytest.mark.asyncio
    async def test_clear(self) -> None:
        stream = EventStream("s")
        for i in range(3):
            await stream.publish({"v": i})
        assert stream.clear() == 3
        assert stream.size() == 0
        assert stream.last_offset() == 0

    @pytest.mark.asyncio
    async def test_status(self) -> None:
        stream = EventStream("s")
        await stream.publish({"v": 1})
        status = stream.status()
        assert status["name"] == "s"
        assert status["events"] == 1
        assert status["last_offset"] == 1

    @pytest.mark.asyncio
    async def test_with_engine_metrics(self, engine: DataEngine) -> None:
        stream = EventStream("s", engine=engine)
        await stream.publish({"v": 1})
        assert engine.metrics.get_counter("streaming.published", {"stream": "s"}) >= 1


class TestStreamManager:
    @pytest.mark.asyncio
    async def test_create_get_list_remove(self) -> None:
        manager = StreamManager()
        stream = manager.create("orders")
        assert manager.get("orders") is stream
        assert manager.names() == ["orders"]
        assert manager.list() == [stream]
        assert manager.remove("orders") is True
        assert manager.remove("orders") is False

    @pytest.mark.asyncio
    async def test_publish_via_manager(self) -> None:
        manager = StreamManager()
        manager.create("orders")
        event = await manager.publish("orders", {"sku": "A"})
        assert event.stream == "orders"

    @pytest.mark.asyncio
    async def test_publish_missing_raises(self) -> None:
        manager = StreamManager()
        with pytest.raises(ValueError):
            await manager.publish("nope", {})

    @pytest.mark.asyncio
    async def test_custom_buffer_size(self) -> None:
        manager = StreamManager(default_buffer_size=100)
        stream = manager.create("small", buffer_size=2)
        for i in range(5):
            await stream.publish({"v": i})
        assert stream.size() == 2

    @pytest.mark.asyncio
    async def test_manager_status(self) -> None:
        manager = StreamManager()
        manager.create("a")
        manager.create("b")
        status = manager.status()
        assert status["count"] == 2
        assert set(status["streams"]) == {"a", "b"}

    @pytest.mark.asyncio
    async def test_manager_with_engine(self, engine: DataEngine) -> None:
        manager = StreamManager(engine=engine)
        manager.create("m")
        await manager.publish("m", {"v": 1})
        assert engine.metrics.get_counter("streaming.published", {"stream": "m"}) >= 1
