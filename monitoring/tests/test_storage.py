from __future__ import annotations

import pytest

from SuperDev.monitoring.storage.storage_manager import StorageManager
from SuperDev.monitoring.storage.memory_storage import MemoryStorage
from SuperDev.monitoring.storage.file_storage import FileStorage
from SuperDev.monitoring.storage.sqlite_storage import SqliteStorage
from SuperDev.monitoring.storage.retention_policy import RetentionPolicy
from SuperDev.monitoring.storage.storage_metrics import StorageMetrics


class TestMemoryStorage:
    def test_store_and_retrieve(self) -> None:
        s = MemoryStorage()
        s.store("key1", {"val": 42})
        assert s.retrieve("key1") == {"val": 42}
        assert s.retrieve("missing") is None
        assert s.delete("key1") is True
        assert s.delete("missing") is False

    def test_list_keys(self) -> None:
        s = MemoryStorage()
        s.store("a", {})
        s.store("b", {})
        assert len(s.list_keys()) == 2


class TestStorageManager:
    def test_with_memory_backend(self) -> None:
        mgr = StorageManager(backend=MemoryStorage())
        mgr.store("k", {"data": 1})
        assert mgr.retrieve("k") == {"data": 1}
        assert mgr.list_keys() == ["k"]

    def test_no_backend(self) -> None:
        mgr = StorageManager()
        assert mgr.retrieve("k") is None
        assert mgr.delete("k") is False
        assert mgr.list_keys() == []


class TestRetentionPolicy:
    def test_expiry(self) -> None:
        import time
        policy = RetentionPolicy(max_age_days=1)
        old = time.time() - 86400 * 10
        recent = time.time()
        assert policy.is_expired(old)
        assert not policy.is_expired(recent)

    def test_apply_filter(self) -> None:
        import time
        policy = RetentionPolicy(max_age_days=1)
        data = {
            "old": {"timestamp": time.time() - 86400 * 10},
            "new": {"timestamp": time.time()},
        }
        filtered = policy.apply(data)
        assert "new" in filtered
        assert "old" not in filtered


class TestStorageMetrics:
    def test_metrics(self) -> None:
        m = StorageMetrics()
        m.record_write()
        m.record_read()
        m.record_delete()
        m.record_write(error=True)
        data = m.collect()
        assert data["write_count"] == 2
        assert data["write_errors"] == 1
        assert data["read_count"] == 1
        assert data["delete_count"] == 1


class TestFileStorage:
    def test_store_and_delete(self, tmp_path: str) -> None:
        import os
        path = str(tmp_path)
        s = FileStorage(directory=path)
        s.store("test_key", {"a": 1})
        assert s.retrieve("test_key") == {"a": 1}
        assert s.delete("test_key") is True


class TestSqliteStorage:
    def test_store_and_retrieve(self) -> None:
        import tempfile
        import os
        db = os.path.join(tempfile.gettempdir(), "test_monitoring.db")
        try:
            s = SqliteStorage(db_path=db)
            s.store("k1", {"x": 10})
            assert s.retrieve("k1") == {"x": 10}
            assert s.delete("k1") is True
        finally:
            s.close()
            if os.path.exists(db):
                os.remove(db)
