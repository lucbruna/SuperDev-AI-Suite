"""Tests for the logging subpackage (Volume 37, Fase 4)."""

from __future__ import annotations

import pytest

from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.logging import LoggingEngine


@pytest.fixture()
def logging_engine() -> LoggingEngine:
    return LoggingEngine()


class TestLogCollector:
    def test_collect(self, logging_engine: LoggingEngine) -> None:
        entry = logging_engine.collect("api", "request ok")
        assert entry.source == "api"
        assert entry.level == "info"
        assert logging_engine.collector.count() == 1


class TestLogIndex:
    def test_search_by_token(self, logging_engine: LoggingEngine) -> None:
        logging_engine.collect("api", "timeout on checkout")
        logging_engine.collect("api", "checkout succeeded")
        hits = logging_engine.search("checkout")
        assert len(hits) == 2

    def test_search_and_filter(self, logging_engine: LoggingEngine) -> None:
        logging_engine.collect("api", "timeout on checkout", level="error")
        logging_engine.collect("api", "checkout ok", level="info")
        hits = logging_engine.search("checkout", level="error")
        assert len(hits) == 1
        assert hits[0].level == "error"

    def test_search_by_source(self, logging_engine: LoggingEngine) -> None:
        logging_engine.collect("api", "timeout")
        logging_engine.collect("worker", "timeout")
        hits = logging_engine.search("timeout", source="worker")
        assert len(hits) == 1
        assert hits[0].source == "worker"

    def test_empty_query(self, logging_engine: LoggingEngine) -> None:
        logging_engine.collect("api", "anything")
        assert logging_engine.search("") == []


class TestLogAnalyzer:
    def test_error_rate(self, logging_engine: LoggingEngine) -> None:
        logging_engine.collect("api", "a", level="error")
        logging_engine.collect("api", "b", level="info")
        assert logging_engine.analyzer.error_rate(
            logging_engine.collector.entries()) == 0.5

    def test_top_errors(self, logging_engine: LoggingEngine) -> None:
        for _ in range(3):
            logging_engine.collect("api", "db timeout", level="error")
        logging_engine.collect("api", "oom", level="error")
        top = logging_engine.analyzer.top_errors(
            logging_engine.collector.entries())
        assert top[0] == "db timeout"

    def test_summary(self, logging_engine: LoggingEngine) -> None:
        logging_engine.collect("api", "a", level="error")
        logging_engine.collect("api", "b", level="warning")
        logging_engine.collect("api", "c")
        summary = logging_engine.analyzer.summary(
            logging_engine.collector.entries())
        assert summary["total"] == 3
        assert summary["errors"] == 1
        assert summary["warnings"] == 1


class TestLoggingEngine:
    def test_collect_event_and_metric(self,
                                      logging_engine: LoggingEngine) -> None:
        events = DevopsEvents()
        logging_engine.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.LOG_COLLECTED, seen.append)
        entry = logging_engine.collect("api", "hello")
        assert entry.source == "api"
        assert len(seen) == 1
        assert logging_engine.metrics.count("devops.logs.collected") == 1

    def test_search(self, logging_engine: LoggingEngine) -> None:
        logging_engine.collect("api", "payment failed", level="error")
        assert len(logging_engine.search("payment failed")) == 1

    def test_analyze_uses_collected(self, logging_engine: LoggingEngine) -> None:
        logging_engine.collect("api", "x", level="error")
        summary = logging_engine.analyze()
        assert summary["errors"] == 1

    def test_stats(self, logging_engine: LoggingEngine) -> None:
        logging_engine.collect("api", "hello world")
        stats = logging_engine.stats()
        assert stats["entries"] == 1
        assert stats["indexed_tokens"] >= 1
