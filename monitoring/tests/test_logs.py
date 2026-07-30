from __future__ import annotations

import pytest

from SuperDev.monitoring.logs.log_engine import LogEngine, LogConfig
from SuperDev.monitoring.logs.structured_logger import StructuredLogger
from SuperDev.monitoring.logs.rotation import LogRotation
from SuperDev.monitoring.logs.retention import LogRetention
from SuperDev.monitoring.logs.search import LogSearch
from SuperDev.monitoring.logs.indexing import LogIndex
from SuperDev.monitoring.monitoring_models import LogLevel, LogEntry


class TestLogEngine:
    def test_engine_defaults(self) -> None:
        engine = LogEngine(LogConfig())
        assert engine is not None

    def test_log_methods(self) -> None:
        engine = LogEngine(LogConfig())
        engine.info("test", source="test")
        engine.error("err", exception="err")
        entries = engine.get_entries()
        assert len(entries) == 2


class TestStructuredLogger:
    def test_log(self) -> None:
        logger = StructuredLogger("test")
        logger.info("msg", extra={"key": "val"})
        assert len(logger._entries) == 1


class TestLogRotation:
    def test_rotation(self) -> None:
        rot = LogRotation(max_bytes=100, backup_count=3)
        assert rot.max_bytes == 100


class TestLogRetention:
    def test_retention(self) -> None:
        ret = LogRetention(max_days=7)
        assert ret.max_days == 7


class TestLogSearch:
    def test_search(self) -> None:
        search = LogSearch()
        entries = [
            LogEntry(message="error occurred", level=LogLevel.ERROR, logger="test"),
            LogEntry(message="info msg", level=LogLevel.INFO, logger="test"),
        ]
        search.index(entries)
        results = search.search("error")
        assert len(results) == 1


class TestLogIndex:
    def test_index_and_query(self) -> None:
        index = LogIndex(":memory:")
        entry = LogEntry(message="test msg", level=LogLevel.INFO, logger="test")
        index.index(entry)
        results = index.query(level="INFO")
        assert len(results) >= 1
