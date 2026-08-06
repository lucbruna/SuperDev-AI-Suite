"""Tests for the persistent memory store (Phase F)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.memory import MemoryEntry, MemoryStore


class TestMemoryStore:
    def test_put_get_contains(self):
        store = MemoryStore()
        store.put("k", {"a": 1}, tags=["x"])
        assert store.get("k") == {"a": 1}
        assert store.contains("k")
        assert store.entry("k").tags == ["x"]

    def test_overwrite(self):
        store = MemoryStore()
        store.put("k", 1)
        store.put("k", 2)
        assert store.get("k") == 2
        assert store.keys() == ["k"]

    def test_get_default(self):
        assert MemoryStore().get("missing", "d") == "d"

    def test_delete(self):
        store = MemoryStore()
        store.put("k", 1)
        assert store.delete("k") is True
        assert store.delete("k") is False
        assert not store.contains("k")

    def test_clear_and_stats(self):
        store = MemoryStore()
        store.put("a", 1)
        store.put("b", 2)
        assert store.stats()["count"] == 2
        store.clear()
        assert store.stats()["count"] == 0

    def test_entries_keep_insertion_order(self):
        store = MemoryStore()
        store.put("b", 1)
        store.put("a", 2)
        assert [entry.key for entry in store.entries()] == ["b", "a"]

    def test_save_load_roundtrip(self, tmp_path):
        path = tmp_path / "mem.json"
        store = MemoryStore(path)
        store.put("k", {"n": 1}, tags=["t"])
        store.save()
        loaded = MemoryStore(path)
        assert loaded.get("k") == {"n": 1}
        assert loaded.entry("k").tags == ["t"]
        assert loaded.entry("k").timestamp == store.entry("k").timestamp

    def test_load_missing_file(self, tmp_path):
        assert MemoryStore(tmp_path / "nope.json").keys() == []

    def test_save_without_path_raises(self):
        with pytest.raises(ValueError):
            MemoryStore().save()

    def test_atomic_write_leaves_no_tmp(self, tmp_path):
        path = tmp_path / "mem.json"
        store = MemoryStore(path)
        store.put("k", 1)
        store.save()
        leftovers = [p for p in tmp_path.iterdir() if p.suffix == ".tmp"]
        assert leftovers == []

    def test_save_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "nested" / "dir" / "mem.json"
        store = MemoryStore(path)
        store.put("k", 1)
        store.save()
        assert path.exists()

    def test_entry_dataclass(self):
        entry = MemoryEntry(key="k", value=1, tags=["a"])
        assert entry.to_dict()["key"] == "k"
        restored = MemoryEntry.from_dict(entry.to_dict())
        assert restored.value == 1
        assert restored.tags == ["a"]
