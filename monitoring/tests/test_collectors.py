from __future__ import annotations

import pytest

from SuperDev.monitoring.collectors.system_collector import SystemCollector
from SuperDev.monitoring.collectors.process_collector import ProcessCollector
from SuperDev.monitoring.collectors.network_collector import NetworkCollector
from SuperDev.monitoring.collectors.disk_collector import DiskCollector
from SuperDev.monitoring.collectors.database_collector import DatabaseCollector
from SuperDev.monitoring.collectors.api_collector import ApiCollector
from SuperDev.monitoring.collectors.llm_collector import LlmCollector
from SuperDev.monitoring.collectors.cache_collector import CacheCollector
from SuperDev.monitoring.collectors.event_collector import EventCollector


class TestSystemCollector:
    def test_collect(self) -> None:
        c = SystemCollector()
        data = c.collect()
        assert "platform" in data
        assert "cpus" in data


class TestProcessCollector:
    def test_collect(self) -> None:
        c = ProcessCollector()
        data = c.collect()
        assert "pid" in data
        assert "name" in data


class TestNetworkCollector:
    def test_collect(self) -> None:
        c = NetworkCollector()
        data = c.collect()
        assert "bytes_sent" in data


class TestDiskCollector:
    def test_collect(self) -> None:
        c = DiskCollector()
        data = c.collect()
        assert "total" in data


class TestDatabaseCollector:
    def test_record_and_collect(self) -> None:
        c = DatabaseCollector()
        c.record_query(0.5)
        c.record_error()
        data = c.collect()
        assert data["query_count"] == 1
        assert data["error_count"] == 1


class TestApiCollector:
    def test_record_and_collect(self) -> None:
        c = ApiCollector()
        c.record_request(0.2, 200)
        c.record_request(0.5, 500)
        data = c.collect()
        assert data["request_count"] == 2
        assert data["error_count"] == 1


class TestLlmCollector:
    def test_record_and_collect(self) -> None:
        c = LlmCollector()
        c.record_request(1.0, tokens=100)
        data = c.collect()
        assert data["request_count"] == 1


class TestCacheCollector:
    def test_hit_rate(self) -> None:
        c = CacheCollector()
        c.record_hit()
        c.record_hit()
        c.record_miss()
        data = c.collect()
        assert data["hit_rate"] == 2 / 3


class TestEventCollector:
    def test_record_and_collect(self) -> None:
        c = EventCollector()
        c.record_event("login")
        c.record_event("login")
        c.record_event("logout")
        data = c.collect()
        assert data["total_events"] == 3
        assert data["unique_types"] == 2
