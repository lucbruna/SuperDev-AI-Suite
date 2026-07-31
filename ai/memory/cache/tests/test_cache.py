from __future__ import annotations

from ..cache_engine import CacheEngine
from ..cache_entry import CacheEntry
from ..cache_policy import CachePolicy
from ..cache_serializer import CacheSerializer
from ..cache_store import CacheStore
from ..cache_validator import CacheValidator
from ..distributed_cache import DistributedCache
from ..lru_cache import LRUCache
from ..ttl_cache import TTLCache


class TestCacheEntry:
    def test_create(self) -> None:
        e = CacheEntry("k1", "v1", 60.0)
        assert e.key == "k1"
        assert e.value == "v1"
        assert e.ttl == 60.0
        assert e.access_count >= 1

    def test_is_expired(self) -> None:
        e = CacheEntry("k", "v", -1.0)
        assert e.is_expired

    def test_age(self) -> None:
        e = CacheEntry("k", "v", 100.0)
        assert e.age >= 0

    def test_to_dict(self) -> None:
        e = CacheEntry("k", "v", 60.0)
        d = e.to_dict()
        assert d["key"] == "k"

    def test_from_dict(self) -> None:
        e = CacheEntry.from_dict({"key": "k", "value": "v", "ttl": 60.0})
        assert e.key == "k"
        assert e.value == "v"


class TestCachePolicy:
    def test_defaults(self) -> None:
        p = CachePolicy()
        assert p.eviction_strategy == "lru"
        assert p.max_size == 1000

    def test_should_evict(self) -> None:
        p = CachePolicy(max_size=2)
        assert p.should_evict(2)
        assert not p.should_evict(1)

    def test_select_victim_lru(self) -> None:
        p = CachePolicy()
        entries = [
            {"key": "a", "accessed_at": 1, "access_count": 5, "created_at": 1},
            {"key": "b", "accessed_at": 2, "access_count": 3, "created_at": 2},
        ]
        assert p.select_victim(entries) == "a"

    def test_select_victim_lfu(self) -> None:
        p = CachePolicy(eviction_strategy="lfu")
        entries = [
            {"key": "a", "accessed_at": 1, "access_count": 5, "created_at": 1},
            {"key": "b", "accessed_at": 2, "access_count": 3, "created_at": 2},
        ]
        assert p.select_victim(entries) == "b"


class TestCacheStore:
    def setup_method(self) -> None:
        self.store = CacheStore("test")

    def test_set_get(self) -> None:
        self.store.set("k", "v")
        assert self.store.get("k") == "v"

    def test_get_missing(self) -> None:
        assert self.store.get("missing") is None

    def test_delete(self) -> None:
        self.store.set("k", "v")
        assert self.store.delete("k") is True
        assert self.store.get("k") is None

    def test_clear(self) -> None:
        self.store.set("a", 1)
        self.store.set("b", 2)
        self.store.clear()
        assert self.store.size == 0

    def test_keys(self) -> None:
        self.store.set("k", "v")
        assert "k" in self.store


class TestLRUCache:
    def setup_method(self) -> None:
        self.lru = LRUCache(max_size=3)

    def test_set_get(self) -> None:
        self.lru.set("k", "v")
        assert self.lru.get("k") == "v"

    def test_eviction(self) -> None:
        self.lru.set("a", 1)
        self.lru.set("b", 2)
        self.lru.set("c", 3)
        self.lru.set("d", 4)
        assert self.lru.size == 3
        assert self.lru.get("a") is None

    def test_touch(self) -> None:
        self.lru.set("a", 1)
        self.lru.set("b", 2)
        self.lru.set("c", 3)
        self.lru.get("a")
        self.lru.set("d", 4)
        assert self.lru.get("b") is None

    def test_clear(self) -> None:
        self.lru.set("a", 1)
        self.lru.clear()
        assert self.lru.size == 0


class TestTTLCache:
    def setup_method(self) -> None:
        self.ttl = TTLCache(default_ttl=60.0, max_size=100)

    def test_set_get(self) -> None:
        self.ttl.set("k", "v")
        assert self.ttl.get("k") == "v"

    def test_expired(self) -> None:
        cache = TTLCache(default_ttl=-1.0)
        cache.set("k", "v")
        assert cache.get("k") is None

    def test_remaining_ttl(self) -> None:
        self.ttl.set("k", "v", 100.0)
        r = self.ttl.remaining_ttl("k")
        assert r is not None and r > 0

    def test_remaining_ttl_missing(self) -> None:
        assert self.ttl.remaining_ttl("missing") is None

    def test_clear(self) -> None:
        self.ttl.set("a", 1)
        self.ttl.clear()
        assert self.ttl.size == 0


class TestDistributedCache:
    def setup_method(self) -> None:
        self.node_a = DistributedCache("node_a")
        self.node_b = DistributedCache("node_b")

    def test_set_get(self) -> None:
        self.node_a.set("k", "v")
        assert self.node_a.get("k") == "v"

    def test_sync(self) -> None:
        self.node_a.set("k", "v1")
        self.node_b.set("k", "v2")
        count = self.node_a.sync(self.node_b)
        assert count >= 1

    def test_delete(self) -> None:
        self.node_a.set("k", "v")
        assert self.node_a.delete("k") is True
        assert self.node_a.get("k") is None


class TestCacheSerializer:
    def test_serialize_deserialize(self) -> None:
        data = {"a": 1, "b": [2, 3]}
        s = CacheSerializer.serialize(data)
        d = CacheSerializer.deserialize(s)
        assert d == data

    def test_serialize_entry(self) -> None:
        e = CacheSerializer.serialize_entry("k", "v", 60.0)
        assert e["key"] == "k"


class TestCacheValidator:
    def test_validate_key(self) -> None:
        assert CacheValidator.validate_key("valid")
        assert not CacheValidator.validate_key("")
        assert not CacheValidator.validate_key(123)

    def test_validate_ttl(self) -> None:
        assert CacheValidator.validate_ttl(60.0)
        assert not CacheValidator.validate_ttl(-1)

    def test_validate_value(self) -> None:
        assert CacheValidator.validate_value("x")
        assert not CacheValidator.validate_value(None)

    def test_sanitize_key(self) -> None:
        assert CacheValidator.sanitize_key(" my key ") == "my_key"


class TestCacheEngine:
    def setup_method(self) -> None:
        self.engine = CacheEngine()
        self.store = CacheStore("default")
        self.engine.register_store("default", self.store)

    def test_set_get(self) -> None:
        self.engine.set("k", "v")
        assert self.engine.get("k") == "v"

    def test_delete(self) -> None:
        self.engine.set("k", "v")
        assert self.engine.delete("k") is True

    def test_clear(self) -> None:
        self.engine.set("a", 1)
        self.engine.clear()
        assert self.engine.get("a") is None

    def test_stats(self) -> None:
        s = self.engine.stats()
        assert s["stores"] == 1
