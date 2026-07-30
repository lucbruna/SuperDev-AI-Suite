from __future__ import annotations

import asyncio

import pytest  # type: ignore[import-untyped]

from SuperDev.database.cache import MemoryCacheEngine


@pytest.fixture()
def cache() -> MemoryCacheEngine:
    return MemoryCacheEngine()


@pytest.mark.asyncio()
async def test_set_and_get(cache: MemoryCacheEngine) -> None:
    await cache.set("key1", "value1")
    val = await cache.get("key1")
    assert val == "value1"


@pytest.mark.asyncio()
async def test_get_missing(cache: MemoryCacheEngine) -> None:
    val = await cache.get("nonexistent")
    assert val is None


@pytest.mark.asyncio()
async def test_ttl_expiry(cache: MemoryCacheEngine) -> None:
    await cache.set("short", "lived", ttl=0)  # 0 = expired immediately
    val = await cache.get("short")
    assert val is None


@pytest.mark.asyncio()
async def test_delete(cache: MemoryCacheEngine) -> None:
    await cache.set("del_me", "value")
    existed = await cache.delete("del_me")
    assert existed is True
    assert await cache.get("del_me") is None


@pytest.mark.asyncio()
async def test_delete_missing(cache: MemoryCacheEngine) -> None:
    existed = await cache.delete("nothing")
    assert existed is False


@pytest.mark.asyncio()
async def test_exists(cache: MemoryCacheEngine) -> None:
    await cache.set("present", "here")
    assert await cache.exists("present") is True
    assert await cache.exists("missing") is False


@pytest.mark.asyncio()
async def test_clear(cache: MemoryCacheEngine) -> None:
    await cache.set("a", 1)
    await cache.set("b", 2)
    await cache.clear()
    assert await cache.get("a") is None
    assert await cache.get("b") is None
    assert await cache.size() == 0


@pytest.mark.asyncio()
async def test_size(cache: MemoryCacheEngine) -> None:
    assert await cache.size() == 0
    await cache.set("x", 10)
    assert await cache.size() == 1
    await cache.set("y", 20)
    assert await cache.size() == 2


@pytest.mark.asyncio()
async def test_overwrite(cache: MemoryCacheEngine) -> None:
    await cache.set("k", "old")
    await cache.set("k", "new")
    assert await cache.get("k") == "new"


@pytest.mark.asyncio()
async def test_concurrent_access(cache: MemoryCacheEngine) -> None:
    async def worker(n: int) -> None:
        for i in range(10):
            await cache.set(f"w{n}_k{i}", i)

    await asyncio.gather(worker(1), worker(2), worker(3))
    assert await cache.size() == 30
