"""Unit tests for phase 6 — storage, snapshots and pipeline persistence.

Covers the JSON file store and SQLite store (round-trip, existence, delete,
prefix listing, clear), the snapshot manager (save/load/list/rotation, capture
and restore of context artifacts) and the runtime wiring that autosaves a
snapshot at the end of every pipeline run.
"""
from __future__ import annotations

import pytest

from modules.ai_code_knowledge_graph.config.knowledge_config import KnowledgeConfig
from modules.ai_code_knowledge_graph.core.knowledge_context import KnowledgeContext
from modules.ai_code_knowledge_graph.core.knowledge_runtime import KnowledgeRuntime
from modules.ai_code_knowledge_graph.embeddings.vector_store import MemoryVectorStore
from modules.ai_code_knowledge_graph.storage import (
    JsonFileStore,
    SnapshotManager,
    SqliteStore,
    build_store,
)


# ------------------------------------------------------------------ fixtures
def _config(tmp_path, backend: str = "sqlite") -> KnowledgeConfig:
    config = KnowledgeConfig()
    config.storage_backend = backend
    config.scanner.project_root = str(tmp_path)
    config.scanner.project_dirs = ("src",)
    config.resolve()
    return config


def _store_with_data(store) -> None:
    store.save("doc:one", {"name": "one", "value": 1})
    store.save("doc:two", {"name": "two", "value": 2})
    store.save("meta:x", {"name": "x"})


# ------------------------------------------------------------- json file store
class TestJsonFileStore:
    def test_round_trip(self, tmp_path) -> None:
        store = JsonFileStore(tmp_path / "data")
        store.save("doc:one", {"name": "one", "value": 1})
        assert store.load("doc:one") == {"name": "one", "value": 1}

    def test_load_missing_returns_none(self, tmp_path) -> None:
        assert JsonFileStore(tmp_path / "data").load("nope") is None

    def test_exists_delete(self, tmp_path) -> None:
        store = JsonFileStore(tmp_path / "data")
        store.save("a", {"v": 1})
        assert store.exists("a")
        assert store.delete("a") is True
        assert store.delete("a") is False
        assert not store.exists("a")

    def test_list_keys_with_prefix(self, tmp_path) -> None:
        store = JsonFileStore(tmp_path / "data")
        _store_with_data(store)
        assert store.list_keys("doc:") == ["doc:one", "doc:two"]
        assert store.list_keys() == ["doc:one", "doc:two", "meta:x"]

    def test_clear(self, tmp_path) -> None:
        store = JsonFileStore(tmp_path / "data")
        _store_with_data(store)
        store.clear()
        assert store.list_keys() == []

    def test_sanitizes_keys(self, tmp_path) -> None:
        store = JsonFileStore(tmp_path / "data")
        store.save("a/b c", {"v": 1})
        assert store.load("a/b c") == {"v": 1}
        assert store.exists("a/b c")


# ---------------------------------------------------------------- sqlite store
class TestSqliteStore:
    def test_round_trip(self, tmp_path) -> None:
        store = SqliteStore(tmp_path / "data.db")
        store.save("doc:one", {"name": "one", "value": 1})
        assert store.load("doc:one") == {"name": "one", "value": 1}
        store.close()

    def test_load_missing_returns_none(self, tmp_path) -> None:
        store = SqliteStore(tmp_path / "data.db")
        assert store.load("nope") is None
        store.close()

    def test_upsert_and_delete(self, tmp_path) -> None:
        store = SqliteStore(tmp_path / "data.db")
        store.save("a", {"v": 1})
        store.save("a", {"v": 2})
        assert store.load("a") == {"v": 2}
        assert store.delete("a") is True
        assert store.delete("a") is False
        store.close()

    def test_list_keys_with_prefix(self, tmp_path) -> None:
        store = SqliteStore(tmp_path / "data.db")
        _store_with_data(store)
        assert store.list_keys("doc:") == ["doc:one", "doc:two"]
        assert store.list_keys() == ["doc:one", "doc:two", "meta:x"]
        store.close()

    def test_clear(self, tmp_path) -> None:
        store = SqliteStore(tmp_path / "data.db")
        _store_with_data(store)
        store.clear()
        assert store.list_keys() == []
        store.close()


# ---------------------------------------------------------- snapshot manager
class TestSnapshotManager:
    def test_save_and_load(self, tmp_path) -> None:
        manager = SnapshotManager(JsonFileStore(tmp_path / "data"))
        snapshot_id = manager.save({"graph": {"nodes": 3}}, tag="pipeline")
        assert snapshot_id.startswith("snapshot_")
        document = manager.load(snapshot_id)
        assert document["meta"]["tag"] == "pipeline"
        assert document["payload"] == {"graph": {"nodes": 3}}
        assert manager.load_payload(snapshot_id) == {"graph": {"nodes": 3}}

    def test_list_newest_first(self, tmp_path) -> None:
        manager = SnapshotManager(JsonFileStore(tmp_path / "data"))
        first = manager.save({"n": 1}, tag="a")
        second = manager.save({"n": 2}, tag="b")
        snapshots = manager.list()
        assert [s["id"] for s in snapshots] == [second, first]
        assert snapshots[0]["tag"] == "b"
        assert manager.count() == 2

    def test_delete(self, tmp_path) -> None:
        manager = SnapshotManager(JsonFileStore(tmp_path / "data"))
        snapshot_id = manager.save({"n": 1})
        assert manager.delete(snapshot_id) is True
        assert manager.count() == 0

    def test_rotation_keeps_max_snapshots(self, tmp_path) -> None:
        manager = SnapshotManager(JsonFileStore(tmp_path / "data"), max_snapshots=2)
        for index in range(4):
            manager.save({"n": index}, tag=f"run-{index}")
        snapshots = manager.list()
        assert manager.count() == 2
        assert {s["tag"] for s in snapshots} == {"run-2", "run-3"}

    def test_capture_serializes_artifacts(self, tmp_path) -> None:
        ctx = KnowledgeContext(config=_config(tmp_path))
        ctx.memory.put("knowledge_document", {"project_root": "/tmp", "files": []})
        store = MemoryVectorStore()
        store.add("file:a.py", [1.0, 0.0], {"kind": "file"})
        ctx.memory.put("vector_store", store)
        payload = SnapshotManager(JsonFileStore(tmp_path / "data")).capture(ctx)
        assert payload["knowledge_document"] == {"project_root": "/tmp", "files": []}
        assert payload["vector_store"]["file:a.py"]["vector"] == [1.0, 0.0]

    def test_restore_replays_payload(self, tmp_path) -> None:
        manager = SnapshotManager(JsonFileStore(tmp_path / "data"))
        snapshot_id = manager.save({"knowledge_document": {"files": [1]}}, tag="restore")
        target = KnowledgeContext(config=_config(tmp_path))
        manager.restore(target, manager.load(snapshot_id))
        assert target.memory.get("knowledge_document") == {"files": [1]}


# ---------------------------------------------------------------- build store
class TestBuildStore:
    def test_sqlite_backend(self, tmp_path) -> None:
        assert isinstance(build_store(_config(tmp_path, "sqlite")), SqliteStore)

    def test_memory_backend_falls_back_to_json(self, tmp_path) -> None:
        assert isinstance(build_store(_config(tmp_path, "memory")), JsonFileStore)


# ------------------------------------------------------------ runtime wiring
class TestRuntimeSnapshot:
    def _runtime(self, tmp_path, autosave: bool = True) -> KnowledgeRuntime:
        root = tmp_path / "fixture"
        (root / "src").mkdir(parents=True)
        (root / "src" / "app.py").write_text("def main():\n    return 1\n", encoding="utf-8")
        config = _config(root)
        config.autosave_snapshot = autosave
        return KnowledgeRuntime(config)

    def test_pipeline_autosaves_snapshot(self, tmp_path) -> None:
        runtime = self._runtime(tmp_path)
        summary = runtime.pipeline.run(runtime.context)
        assert "snapshot" in [stage["name"] for stage in summary["stages"]]
        assert runtime.snapshots.count() == 1
        assert runtime.status()["snapshots"] == 1
        assert runtime.context.stats.get("snapshots_saved") == 1

    def test_pipeline_skips_when_autosave_disabled(self, tmp_path) -> None:
        runtime = self._runtime(tmp_path, autosave=False)
        runtime.pipeline.run(runtime.context)
        assert runtime.snapshots.count() == 0

    def test_snapshot_file_persisted(self, tmp_path) -> None:
        runtime = self._runtime(tmp_path)
        runtime.pipeline.run(runtime.context)
        db_file = tmp_path / "fixture" / ".superdev" / "ai_code_knowledge_graph" / "knowledge_graph.db"
        assert db_file.exists()
